"""
Sample order generator for real-time demo
Generates random orders to populate the exchange
"""

import socket
import time
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fix_engine import FIXEngine


class OrderGenerator:
    """Generates random orders for demonstration."""
    
    SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    def __init__(self, host="127.0.0.1", port=9878):
        self.host = host
        self.port = port
        self.fix_engine = FIXEngine()
        self.order_counter = 1
        self.client = None
    
    def connect(self):
        """Connect to exchange."""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(10)
        self.client.connect((self.host, self.port))
        
        # Send logon
        logon = self.fix_engine.create_logon(30)
        self.client.sendall(logon.encode('utf-8'))
        
        # Receive logon ack
        response = self.client.recv(4096)
        print("✓ Connected to exchange")
    
    def generate_random_order(self):
        """Generate a random order."""
        symbol = random.choice(self.SYMBOLS)
        side = random.choice([FIXEngine.SIDE_BUY, FIXEngine.SIDE_SELL])
        order_type = random.choice([FIXEngine.ORDER_TYPE_LIMIT, FIXEngine.ORDER_TYPE_MARKET])
        qty = random.choice([10, 25, 50, 100, 200])
        
        cl_ord_id = f"GEN{self.order_counter:06d}"
        self.order_counter += 1
        
        # Generate realistic prices based on symbol
        base_prices = {
            "AAPL": 180.0,
            "GOOGL": 140.0,
            "MSFT": 370.0,
            "AMZN": 175.0,
            "TSLA": 245.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        price = round(base_price + random.uniform(-10, 10), 2) if order_type == FIXEngine.ORDER_TYPE_LIMIT else None
        
        order = self.fix_engine.create_new_order_single(
            cl_ord_id=cl_ord_id,
            symbol=symbol,
            side=side,
            order_qty=qty,
            order_type=order_type,
            price=price
        )
        
        return order, {
            'symbol': symbol,
            'side': 'BUY' if side == FIXEngine.SIDE_BUY else 'SELL',
            'type': 'LIMIT' if order_type == FIXEngine.ORDER_TYPE_LIMIT else 'MARKET',
            'qty': qty,
            'price': price
        }
    
    def send_order(self, order_msg):
        """Send order to exchange."""
        try:
            self.client.sendall(order_msg.encode('utf-8'))
            # Receive execution report (with timeout)
            self.client.settimeout(10)
            response = self.client.recv(4096)
            return True
        except socket.timeout:
            print(f"Error sending order: Response timeout (server busy)")
            return False
        except Exception as e:
            print(f"Error sending order: {e}")
            return False
    
    def run_continuous(self, interval=2):
        """Continuously generate orders."""
        print(f"Starting order generation (1 order every {interval} seconds)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                order_msg, order_info = self.generate_random_order()
                
                print(f"Generated: {order_info['side']} {order_info['qty']} {order_info['symbol']} "
                      f"@ {order_info['price'] if order_info['price'] else 'MARKET'} ({order_info['type']})")
                
                if self.send_order(order_msg):
                    print("  ✓ Order sent")
                else:
                    print("  ✗ Failed to send")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\nStopping order generation...")
            self.disconnect()
    
    def disconnect(self):
        """Disconnect from exchange."""
        if self.client:
            try:
                logout = self.fix_engine.create_logout()
                self.client.sendall(logout.encode('utf-8'))
                self.client.close()
                print("✓ Disconnected from exchange")
            except Exception:
                pass


def main():
    """Main entry point."""
    print("="*60)
    print("FIX Exchange Order Generator")
    print("="*60)
    print()
    
    generator = OrderGenerator()
    
    try:
        generator.connect()
        generator.run_continuous(interval=2)  # Generate 1 order every 2 seconds
    except ConnectionRefusedError:
        print("✗ Could not connect to exchange server")
        print("  Make sure the exchange server is running on port 9878")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
