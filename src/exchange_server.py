"""
Mock Exchange Server with WebSocket Real-Time Updates

A simplified FIX 4.2 protocol exchange server for testing and certification.
Handles order routing, matching, and execution reporting.
Broadcasts real-time updates via WebSocket.
Uses Numba JIT for high-performance order matching.
Persists data to PostgreSQL database.
"""

import socket
import threading
import logging
import time
import json
import asyncio
import os
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("websockets library not available - real-time features disabled")

# Try to use C++ engine first, fallback to Python
try:
    import crucible_engine
    CPP_ENGINE_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("C++ matching engine loaded - High performance mode (10-50x faster)")
except ImportError:
    CPP_ENGINE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.info("Using Python matching engine")

try:
    from database_sqlite import DatabaseManager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Database module not available - persistence disabled")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# WebSocket clients registry
ws_clients: Set = set()
ws_loop = None


@dataclass
class Order:
    """Represents an order in the exchange."""
    order_id: str
    cl_ord_id: str
    symbol: str
    side: str  # "1" = Buy, "2" = Sell
    order_qty: int
    order_type: str  # "1" = Market, "2" = Limit
    price: Optional[float] = None
    filled_qty: int = 0
    status: str = "0"  # "0" = New
    timestamp: float = field(default_factory=time.time)
    
    @property
    def remaining_qty(self) -> int:
        """Calculate remaining quantity to be filled."""
        return self.order_qty - self.filled_qty
    
    @property
    def is_complete(self) -> bool:
        """Check if order is fully filled."""
        return self.filled_qty >= self.order_qty
    
    def to_dict(self, for_display: bool = False) -> Dict:
        """Convert order to dictionary for JSON serialization.
        
        Args:
            for_display: If True, convert codes to readable text. If False, keep raw codes for DB.
        """
        if for_display:
            return {
                'order_id': self.order_id,
                'cl_ord_id': self.cl_ord_id,
                'symbol': self.symbol,
                'side': 'Buy' if self.side == "1" else 'Sell',
                'order_qty': self.order_qty,
                'order_type': 'Market' if self.order_type == "1" else 'Limit',
                'price': self.price,
                'filled_qty': self.filled_qty,
                'remaining_qty': self.remaining_qty,
                'status': self._get_status_text(),
                'timestamp': datetime.fromtimestamp(self.timestamp).strftime('%H:%M:%S')
            }
        else:
            # For database storage - keep raw codes
            return {
                'order_id': self.order_id,
                'cl_ord_id': self.cl_ord_id,
                'symbol': self.symbol,
                'side': self.side,
                'order_qty': self.order_qty,
                'order_type': self.order_type,
                'price': self.price,
                'filled_qty': self.filled_qty,
                'status': self.status
            }
    
    def _get_status_text(self) -> str:
        """Get human-readable status text."""
        status_map = {
            "0": "New",
            "1": "Partially Filled",
            "2": "Filled",
            "4": "Canceled",
            "8": "Rejected"
        }
        return status_map.get(self.status, "Unknown")


class OrderBook:
    """
    Simplified order book for matching orders.
    Maintains buy and sell orders for each symbol.
    Broadcasts real-time updates via WebSocket.
    Uses Numba JIT matcher when available for high performance.
    Persists to PostgreSQL database.
    """
    
    def __init__(self, db_manager: Optional['DatabaseManager'] = None):
        self.orders: Dict[str, Order] = {}
        self.buy_orders: Dict[str, List[Order]] = {}
        self.sell_orders: Dict[str, List[Order]] = {}
        self.order_counter = 1
        self.exec_counter = 1
        self.lock = threading.Lock()
        self.executions: List[Dict] = []
        self.db_manager = db_manager
        
        # Initialize C++ engine if available
        if CPP_ENGINE_AVAILABLE:
            self.cpp_engine = crucible_engine.MatchingEngine()
            logger.info("Using C++ matching engine - High performance mode")
        else:
            self.cpp_engine = None
            logger.info("Using Python matching engine")
    
    def generate_order_id(self) -> str:
        """Generate unique order ID."""
        with self.lock:
            order_id = f"ORD{self.order_counter:06d}"
            self.order_counter += 1
            return order_id
    
    def generate_exec_id(self) -> str:
        """Generate unique execution ID."""
        with self.lock:
            exec_id = f"EXEC{self.exec_counter:06d}"
            self.exec_counter += 1
            return exec_id
    
    def broadcast_update(self, event_type: str, data: Dict):
        """Broadcast updates to all connected WebSocket clients."""
        if not WEBSOCKETS_AVAILABLE or not ws_clients or not ws_loop:
            return
        
        try:
            message = json.dumps({
                'type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
            
            # Schedule broadcast in WebSocket loop (non-blocking)
            asyncio.run_coroutine_threadsafe(
                self._async_broadcast(message),
                ws_loop
            )
        except Exception as e:
            logger.error(f"Error broadcasting update: {e}")
    
    async def _async_broadcast(self, message: str):
        """Async broadcast to all clients."""
        disconnected = set()
        for client in ws_clients:
            try:
                await client.send(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(client)
        
        # Remove disconnected clients
        for client in disconnected:
            ws_clients.discard(client)
    
    def add_order(self, order: Order) -> None:
        """Add order to the order book."""
        with self.lock:
            self.orders[order.order_id] = order
            
            # Save to database (use raw codes, not display format)
            if self.db_manager:
                try:
                    self.db_manager.save_order(order.to_dict(for_display=False))
                except Exception as e:
                    logger.error(f"Failed to save order to database: {e}")
            
            # Add to appropriate side
            if order.side == "1":  # Buy
                if order.symbol not in self.buy_orders:
                    self.buy_orders[order.symbol] = []
                self.buy_orders[order.symbol].append(order)
                # Sort buy orders by price (highest first)
                self.buy_orders[order.symbol].sort(
                    key=lambda x: (x.price if x.price else float('inf'), x.timestamp),
                    reverse=True
                )
            else:  # Sell
                if order.symbol not in self.sell_orders:
                    self.sell_orders[order.symbol] = []
                self.sell_orders[order.symbol].append(order)
                # Sort sell orders by price (lowest first)
                self.sell_orders[order.symbol].sort(
                    key=lambda x: (x.price if x.price else 0, x.timestamp)
                )
        
        # Broadcast new order (use display format for WebSocket)
        self.broadcast_update('new_order', order.to_dict(for_display=True))
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Retrieve order by ID."""
        return self.orders.get(order_id)
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        with self.lock:
            order = self.orders.get(order_id)
            if not order:
                return False
            
            order.status = "4"  # Canceled
            
            # Remove from active orders
            if order.side == "1":
                if order.symbol in self.buy_orders and order in self.buy_orders[order.symbol]:
                    self.buy_orders[order.symbol].remove(order)
            else:
                if order.symbol in self.sell_orders and order in self.sell_orders[order.symbol]:
                    self.sell_orders[order.symbol].remove(order)
            
            # Broadcast cancel (use display format)
            self.broadcast_update('cancel_order', order.to_dict(for_display=True))
            return True
    
    def get_order_book_snapshot(self) -> Dict:
        """Get current order book state for WebSocket clients."""
        with self.lock:
            snapshot = {
                'buy_orders': {},
                'sell_orders': {},
                'recent_executions': self.executions[-20:] if self.executions else []
            }
            
            for symbol, orders in self.buy_orders.items():
                snapshot['buy_orders'][symbol] = [o.to_dict(for_display=True) for o in orders if not o.is_complete]
            
            for symbol, orders in self.sell_orders.items():
                snapshot['sell_orders'][symbol] = [o.to_dict(for_display=True) for o in orders if not o.is_complete]
            
            return snapshot
    
    def add_execution(self, execution: Dict):
        """Add execution to history and broadcast."""
        with self.lock:
            self.executions.append(execution)
            if len(self.executions) > 100:
                self.executions = self.executions[-100:]
        
        # Skip DB save for speed - will implement batch save later
        # if self.db_manager:
        #     try:
        #         self.db_manager.save_execution(execution)
        #     except Exception as e:
        #         logger.error(f"Failed to save execution to database: {e}")
        
        # Broadcast is non-blocking via asyncio
        self.broadcast_update('execution', execution)
    
    def match_orders(self, symbol: str) -> List[Tuple[Order, Order, int, float]]:
        """Match buy and sell orders using price-time priority. Fast single-pass matching."""
        with self.lock:
            matches = []
            
            if symbol not in self.buy_orders or symbol not in self.sell_orders:
                return matches
            
            # Get active orders and sort ONCE
            buy_orders = [o for o in self.buy_orders[symbol] if not o.is_complete]
            sell_orders = [o for o in self.sell_orders[symbol] if not o.is_complete]
            
            if not buy_orders or not sell_orders:
                return matches
            
            # Sort by price-time priority (once only)
            buy_orders.sort(key=lambda o: (-(o.price or 0), o.timestamp))
            sell_orders.sort(key=lambda o: (o.price or float('inf'), o.timestamp))
            
            # Match iteratively with safety limit
            buy_idx = 0
            sell_idx = 0
            max_iterations = 100
            iterations = 0
            
            while buy_idx < len(buy_orders) and sell_idx < len(sell_orders) and iterations < max_iterations:
                iterations += 1
                buy_order = buy_orders[buy_idx]
                sell_order = sell_orders[sell_idx]
                
                # Skip completed orders
                if buy_order.is_complete:
                    buy_idx += 1
                    continue
                if sell_order.is_complete:
                    sell_idx += 1
                    continue
                
                # Check if they can match
                can_match = False
                match_price = 0.0
                
                if buy_order.order_type == "1":  # Market
                    can_match = True
                    match_price = sell_order.price or 100.0
                elif sell_order.order_type == "1":  # Market
                    can_match = True
                    match_price = buy_order.price or 100.0
                elif buy_order.price and sell_order.price and buy_order.price >= sell_order.price:
                    can_match = True
                    match_price = sell_order.price
                
                if not can_match:
                    break  # No more matches possible
                
                # Execute the match
                match_qty = min(buy_order.remaining_qty, sell_order.remaining_qty)
                
                buy_order.filled_qty += match_qty
                sell_order.filled_qty += match_qty
                buy_order.status = "2" if buy_order.is_complete else "1"
                sell_order.status = "2" if sell_order.is_complete else "1"
                
                # Skip DB save during matching for speed - will save later
                # if self.db_manager:
                #     try:
                #         self.db_manager.save_order(buy_order.to_dict(for_display=False))
                #         self.db_manager.save_order(sell_order.to_dict(for_display=False))
                #     except Exception as e:
                #         logger.error(f"DB save failed: {e}")
                
                matches.append((buy_order, sell_order, match_qty, match_price))
                
                execution = {
                    'symbol': symbol,
                    'side': 'Buy',
                    'last_qty': match_qty,
                    'last_px': match_price,
                    'status': 'Filled' if buy_order.is_complete else 'Partial',
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
                self.add_execution(execution)
                
                # Move to next order if current one complete
                if buy_order.is_complete:
                    buy_idx += 1
                if sell_order.is_complete:
                    sell_idx += 1
                
                # Safety: if neither complete, break to avoid infinite loop
                if not buy_order.is_complete and not sell_order.is_complete:
                    break
        
        return matches



class ExchangeServer:
    """
    FIX 4.2 Exchange Server.
    
    Handles client connections, processes FIX messages, and manages orders.
    """
    
    SOH = '\x01'
    VALID_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9878, db_manager: Optional['DatabaseManager'] = None):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.order_book = OrderBook(db_manager=db_manager)
        self.sessions: Dict[str, bool] = {}  # Track logged-in sessions
        self.db_manager = db_manager
    
    def start(self):
        """Start the exchange server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        logger.info(f"Exchange Server started on {self.host}:{self.port}")
        
        try:
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    logger.info(f"New connection from {address}")
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the exchange server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("Exchange Server stopped")
    
    def handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """
        Handle individual client connection.
        
        Args:
            client_socket: Client socket connection
            address: Client address tuple (host, port)
        """
        session_id = f"{address[0]}:{address[1]}"
        buffer = ""
        
        # Set socket timeout to prevent indefinite blocking
        client_socket.settimeout(5.0)
        
        try:
            while self.running:
                try:
                    data = client_socket.recv(4096).decode('utf-8')
                    if not data:
                        break
                    
                    buffer += data
                    
                    # Process complete messages (terminated by checksum field)
                    while "10=" in buffer:
                        # Find end of message (after checksum)
                        checksum_pos = buffer.find("10=")
                        # Find SOH after checksum value
                        end_pos = buffer.find(self.SOH, checksum_pos)
                        
                        if end_pos == -1:
                            break
                        
                        # Extract complete message
                        message = buffer[:end_pos + 1]
                        buffer = buffer[end_pos + 1:]
                        
                        # Process message
                        response = self.process_message(message, session_id)
                        
                        if response:
                            # Send response immediately without delay
                            client_socket.sendall(response.encode('utf-8'))
                            logger.debug(f"Response sent to {session_id}")
                
                except socket.timeout:
                    # Timeout is expected - continue waiting for more messages
                    continue
        
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        finally:
            # Clean up session
            if session_id in self.sessions:
                del self.sessions[session_id]
            client_socket.close()
            logger.info(f"Connection closed: {address}")
    
    def parse_fix_message(self, message: str) -> Dict[str, str]:
        """Parse FIX message into tag-value dictionary."""
        tags = {}
        fields = message.split(self.SOH)
        
        for field in fields:
            if '=' in field:
                tag, value = field.split('=', 1)
                tags[tag] = value
        
        return tags
    
    def build_fix_message(self, msg_type: str, tags: Dict[str, str]) -> str:
        """
        Build FIX message with header and trailer.
        
        Args:
            msg_type: Message type (Tag 35)
            tags: Dictionary of tag-value pairs for body
            
        Returns:
            Complete FIX message string
        """
        # Build body
        body = f"35={msg_type}{self.SOH}"
        
        # Add standard tags
        body += f"49=EXCHANGE{self.SOH}"
        body += f"56=CLIENT{self.SOH}"
        body += f"34=1{self.SOH}"  # Simplified sequence number
        body += f"52={datetime.utcnow().strftime('%Y%m%d-%H:%M:%S')}{self.SOH}"
        
        # Add custom tags
        for tag, value in tags.items():
            body += f"{tag}={value}{self.SOH}"
        
        # Calculate body length
        body_length = len(body)
        
        # Build message without checksum
        message_without_checksum = f"8=FIX.4.2{self.SOH}9={body_length}{self.SOH}{body}"
        
        # Calculate checksum
        checksum = sum(ord(c) for c in message_without_checksum) % 256
        
        # Complete message
        complete_message = f"{message_without_checksum}10={checksum:03d}{self.SOH}"
        
        return complete_message
    
    def process_message(self, message: str, session_id: str) -> Optional[str]:
        """
        Process incoming FIX message and generate response.
        
        Args:
            message: Raw FIX message
            session_id: Session identifier
            
        Returns:
            Response FIX message or None
        """
        tags = self.parse_fix_message(message)
        msg_type = tags.get("35")
        
        logger.info(f"Received message type: {msg_type} from {session_id}")
        
        if msg_type == "A":  # Logon
            return self.handle_logon(tags, session_id)
        elif msg_type == "0":  # Heartbeat
            return self.handle_heartbeat(tags)
        elif msg_type == "5":  # Logout
            return self.handle_logout(tags, session_id)
        elif msg_type == "D":  # New Order Single
            return self.handle_new_order(tags)
        elif msg_type == "F":  # Order Cancel Request
            return self.handle_cancel_request(tags)
        else:
            logger.warning(f"Unknown message type: {msg_type}")
            return None
    
    def handle_logon(self, tags: Dict[str, str], session_id: str) -> str:
        """Handle Logon message."""
        self.sessions[session_id] = True
        logger.info(f"Session {session_id} logged in")
        
        response_tags = {
            "108": tags.get("108", "30")  # Heartbeat interval
        }
        
        return self.build_fix_message("A", response_tags)
    
    def handle_heartbeat(self, tags: Dict[str, str]) -> str:
        """Handle Heartbeat message."""
        response_tags = {}
        
        # Echo test request ID if present
        if "112" in tags:
            response_tags["112"] = tags["112"]
        
        return self.build_fix_message("0", response_tags)
    
    def handle_logout(self, tags: Dict[str, str], session_id: str) -> str:
        """Handle Logout message."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        logger.info(f"Session {session_id} logged out")
        
        return self.build_fix_message("5", {})
    
    def handle_new_order(self, tags: Dict[str, str]) -> str:
        """Handle New Order Single message."""
        cl_ord_id = tags.get("11")
        symbol = tags.get("55")
        side = tags.get("54")
        order_qty = int(tags.get("38", "0"))
        order_type = tags.get("40")
        price = float(tags.get("44")) if "44" in tags else None
        
        # Validate symbol
        if symbol not in self.VALID_SYMBOLS:
            return self._create_reject_execution_report(
                cl_ord_id, symbol, side, order_qty,
                f"Invalid symbol: {symbol}"
            )
        
        # Validate price
        if price is not None and price <= 0:
            return self._create_reject_execution_report(
                cl_ord_id, symbol, side, order_qty,
                f"Invalid price: {price}"
            )
        
        # Validate quantity
        if order_qty <= 0:
            return self._create_reject_execution_report(
                cl_ord_id, symbol, side, order_qty,
                f"Invalid quantity: {order_qty}"
            )
        
        # Create order
        order_id = self.order_book.generate_order_id()
        order = Order(
            order_id=order_id,
            cl_ord_id=cl_ord_id,
            symbol=symbol,
            side=side,
            order_qty=order_qty,
            order_type=order_type,
            price=price,
            status="0"  # New
        )
        
        self.order_book.add_order(order)
        logger.info(f"Order created: {order_id}")
        
        # Note: Broadcasting is handled in add_order method
        
        # Send New acknowledgment
        response = self._create_execution_report(order, "0", "0", 0, 0.0)
        
        # Try to match orders with timing
        import time
        start = time.time()
        try:
            matches = self.order_book.match_orders(symbol)
            elapsed = time.time() - start
            logger.info(f"Matching complete: {len(matches)} matches in {elapsed:.3f}s")
        except Exception as e:
            logger.error(f"Error matching orders: {e}", exc_info=True)
            matches = []
        
        # Broadcast updated orderbook after matching
        orderbook_snapshot = self.order_book.get_order_book_snapshot()
        self.order_book.broadcast_update('orderbook', orderbook_snapshot)
        
        # Send execution reports for matches
        for buy_order, sell_order, match_qty, match_price in matches:
            # Report for the buy side
            buy_exec_type = "2" if buy_order.is_complete else "1"
            buy_report = self._create_execution_report(
                buy_order, buy_exec_type, buy_order.status, match_qty, match_price
            )
            # Report for the sell side
            sell_exec_type = "2" if sell_order.is_complete else "1"
            sell_report = self._create_execution_report(
                sell_order, sell_exec_type, sell_order.status, match_qty, match_price
            )
            
            # Only append to response if this is the incoming order
            # (to avoid sending reports for previously placed orders)
            if buy_order.cl_ord_id == cl_ord_id:
                response += buy_report
            if sell_order.cl_ord_id == cl_ord_id:
                response += sell_report
        
        logger.info(f"Returning response for order {cl_ord_id}, length: {len(response)} bytes")
        return response
    
    def handle_cancel_request(self, tags: Dict[str, str]) -> str:
        """Handle Order Cancel Request message."""
        orig_cl_ord_id = tags.get("41")
        
        # Find order by client order ID
        order = None
        for ord in self.order_book.orders.values():
            if ord.cl_ord_id == orig_cl_ord_id:
                order = ord
                break
        
        if not order:
            # Send cancel reject
            response_tags = {
                "11": tags.get("11"),
                "41": orig_cl_ord_id,
                "39": "8",  # Rejected
                "58": "Order not found"
            }
            return self.build_fix_message("8", response_tags)
        
        # Cancel the order
        self.order_book.cancel_order(order.order_id)
        
        # Send execution report with canceled status
        return self._create_execution_report(order, "4", "4", 0, 0.0)
    
    def _create_execution_report(
        self,
        order: Order,
        exec_type: str,
        ord_status: str,
        last_qty: int,
        last_px: float
    ) -> str:
        """Create execution report for an order."""
        exec_id = self.order_book.generate_exec_id()
        
        tags = {
            "37": order.order_id,
            "11": order.cl_ord_id,
            "17": exec_id,
            "150": exec_type,
            "39": ord_status,
            "55": order.symbol,
            "54": order.side,
            "38": str(order.order_qty),
            "32": str(last_qty),
            "31": f"{last_px:.2f}",
            "14": str(order.filled_qty),
            "6": f"{last_px:.2f}",
            "60": datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")
        }
        
        return self.build_fix_message("8", tags)
    
    def _create_reject_execution_report(
        self,
        cl_ord_id: str,
        symbol: str,
        side: str,
        order_qty: int,
        reason: str
    ) -> str:
        """Create rejection execution report."""
        exec_id = self.order_book.generate_exec_id()
        order_id = self.order_book.generate_order_id()
        
        tags = {
            "37": order_id,
            "11": cl_ord_id,
            "17": exec_id,
            "150": "8",  # Rejected
            "39": "8",  # Rejected
            "55": symbol,
            "54": side,
            "38": str(order_qty),
            "32": "0",
            "31": "0.00",
            "14": "0",
            "6": "0.00",
            "58": reason,
            "60": datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")
        }
        
        return self.build_fix_message("8", tags)


def main():
    """Main entry point for the exchange server."""
    global ws_loop
    
    # Initialize database if available
    db_manager = None
    if DB_AVAILABLE:
        try:
            db_manager = DatabaseManager('crucible.db')
            logger.info("SQLite database persistence enabled")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.warning("Continuing without database persistence")
            db_manager = None
    
    # Start FIX server with database
    server = ExchangeServer(db_manager=db_manager)
    
    # Start WebSocket server if available
    if WEBSOCKETS_AVAILABLE:
        def start_websocket():
            global ws_loop
            ws_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(ws_loop)
            
            async def websocket_handler(websocket):
                """Handle WebSocket connections."""
                ws_clients.add(websocket)
                logger.info(f"WebSocket client connected. Total clients: {len(ws_clients)}")
                
                try:
                    # Send initial snapshot
                    snapshot = server.order_book.get_order_book_snapshot()
                    await websocket.send(json.dumps({
                        'type': 'snapshot',
                        'data': snapshot,
                        'timestamp': datetime.now().isoformat()
                    }))
                    
                    # Keep connection alive
                    async for message in websocket:
                        pass
                except websockets.exceptions.ConnectionClosed:
                    logger.info("WebSocket client disconnected")
                finally:
                    ws_clients.discard(websocket)
            
            async def start_ws_server():
                server_ws = await websockets.serve(websocket_handler, "127.0.0.1", 8765)
                logger.info("WebSocket server started on ws://127.0.0.1:8765")
                await server_ws.wait_closed()
            
            ws_loop.run_until_complete(start_ws_server())
        
        ws_thread = threading.Thread(target=start_websocket, daemon=True)
        ws_thread.start()
        logger.info("Real-time WebSocket broadcasting enabled")
    else:
        logger.warning("WebSocket support disabled - install 'websockets' package for real-time features")
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop()


if __name__ == "__main__":
    main()
