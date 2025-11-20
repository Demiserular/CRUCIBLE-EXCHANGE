"""
Quick test to verify the setup works
"""
import sys
import socket
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from fix_engine import FIXEngine

def test_connection():
    """Test basic connection to exchange"""
    print("Testing connection to exchange server...")
    
    try:
        # Connect to exchange
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect(("127.0.0.1", 9878))
        print("✓ Connected to exchange")
        
        # Create FIX engine
        fix = FIXEngine()
        
        # Send logon
        print("\nSending Logon message...")
        logon = fix.create_logon(30)
        client.sendall(logon.encode('utf-8'))
        
        # Receive response
        response = client.recv(4096).decode('utf-8')
        tags = fix.parse_message(response)
        
        if tags.get("35") == "A":
            print("✓ Received Logon acknowledgment")
        else:
            print(f"✗ Unexpected response: {tags.get('35')}")
            return False
        
        # Send new order
        print("\nSending New Order...")
        order = fix.create_new_order_single(
            cl_ord_id="TEST001",
            symbol="AAPL",
            side=FIXEngine.SIDE_BUY,
            order_qty=100,
            order_type=FIXEngine.ORDER_TYPE_LIMIT,
            price=150.00
        )
        client.sendall(order.encode('utf-8'))
        
        # Receive execution report
        response = client.recv(4096).decode('utf-8')
        tags = fix.parse_message(response)
        
        if tags.get("35") == "8":
            print(f"✓ Received Execution Report (Status: {tags.get('39')})")
        else:
            print(f"✗ Unexpected response: {tags.get('35')}")
            return False
        
        # Send logout
        print("\nSending Logout...")
        logout = fix.create_logout()
        client.sendall(logout.encode('utf-8'))
        
        response = client.recv(4096).decode('utf-8')
        tags = fix.parse_message(response)
        
        if tags.get("35") == "5":
            print("✓ Received Logout acknowledgment")
        else:
            print(f"✗ Unexpected response: {tags.get('35')}")
            return False
        
        client.close()
        print("\n✅ All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
