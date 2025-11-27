"""
Flask API Server for Crucible Exchange
Provides HTTP endpoints for historical data retrieval and order submission
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import socket
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from database_sqlite import DatabaseManager
from fix_engine import FIXEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS with explicit configuration for preflight requests
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

# Initialize SQLite database
try:
    db = DatabaseManager('crucible.db')
    logger.info("API connected to SQLite database")
except Exception as e:
    logger.error(f"Failed to connect to database: {e}")
    db = None

# Initialize FIX engine for manual trading
fix_engine = FIXEngine()
exchange_host = '127.0.0.1'
exchange_port = 9878


# Add after_request handler to ensure CORS headers on all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'database': 'connected' if db else 'disconnected'
    })


@app.route('/api/executions', methods=['GET'])
def get_executions():
    """
    Get recent executions.
    Query params:
        - limit: Number of executions to return (default: 100)
    """
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        limit = int(request.args.get('limit', 100))
        executions = db.get_recent_executions(limit=limit)
        return jsonify({
            'executions': executions,
            'count': len(executions)
        })
    except Exception as e:
        logger.error(f"Error fetching executions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders', methods=['GET'])
def get_orders():
    """
    Get open orders.
    Query params:
        - symbol: Filter by symbol (optional)
    """
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        symbol = request.args.get('symbol')
        orders = db.get_open_orders(symbol=symbol)
        return jsonify({
            'orders': orders,
            'count': len(orders)
        })
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/orderbook', methods=['GET'])
def get_orderbook():
    """
    Get current order book grouped by symbol.
    """
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        orders = db.get_open_orders()
        
        # Group by symbol and side
        orderbook = {
            'buy_orders': {},
            'sell_orders': {}
        }
        
        for order in orders:
            symbol = order['symbol']
            # Convert to display format
            display_order = {
                'order_id': order['order_id'],
                'cl_ord_id': order['cl_ord_id'],
                'symbol': order['symbol'],
                'side': 'Buy' if order['side'] == '1' else 'Sell',
                'order_qty': order['order_qty'],
                'order_type': 'Market' if order.get('order_type') == '1' else 'Limit',
                'price': order.get('price'),
                'filled_qty': order.get('filled_qty', 0),
                'status': order.get('status', '0')
            }
            
            if order['side'] == '1':  # Buy
                if symbol not in orderbook['buy_orders']:
                    orderbook['buy_orders'][symbol] = []
                orderbook['buy_orders'][symbol].append(display_order)
            else:  # Sell
                if symbol not in orderbook['sell_orders']:
                    orderbook['sell_orders'][symbol] = []
                orderbook['sell_orders'][symbol].append(display_order)
        
        return jsonify(orderbook)
    except Exception as e:
        logger.error(f"Error fetching orderbook: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get exchange statistics."""
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        stats = db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/submit_order', methods=['POST', 'OPTIONS'])
def submit_order():
    """
    Submit a manual order to the exchange.
    
    Request body:
    {
        "symbol": "AAPL",
        "side": "1",  # 1=Buy, 2=Sell
        "order_qty": 100,
        "order_type": "2",  # 1=Market, 2=Limit
        "price": 150.00  # Required for limit orders
    }
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['symbol', 'side', 'order_qty', 'order_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate limit order has price
        if data['order_type'] == '2' and 'price' not in data:
            return jsonify({'error': 'Price required for limit orders'}), 400
        
        # Generate client order ID
        cl_ord_id = f"MAN{int(os.urandom(4).hex(), 16):08d}"
        
        # Create FIX message
        order_msg = fix_engine.create_new_order_single(
            cl_ord_id=cl_ord_id,
            symbol=data['symbol'],
            side=data['side'],
            order_qty=data['order_qty'],
            order_type=data['order_type'],
            price=data.get('price')
        )
        
        # Connect to exchange and send order
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)  # Allow time for Exchange Server to accept connection
        
        try:
            # Connect
            client.connect((exchange_host, exchange_port))
            
            # Send logon
            logon = fix_engine.create_logon(30)
            client.sendall(logon.encode('utf-8'))
            response = client.recv(8192)
            logger.info(f"Logon response received")
            
            # Send order
            client.sendall(order_msg.encode('utf-8'))
            logger.info(f"Order sent: {cl_ord_id}")
            
            # Receive execution report (may include multiple messages if matched)
            client.settimeout(10)  # Allow time for matching engine to process and respond
            exec_report = client.recv(8192).decode('utf-8')
            logger.info(f"Execution report received")
            
            # Parse response to get order ID - handle multiple messages
            # Split by FIX message delimiter and find the execution report
            tags = {}
            if "35=8" in exec_report:
                # Split potential multiple messages
                messages = exec_report.split("8=FIX.4.2")
                for msg in messages:
                    if msg and "35=8" in msg:
                        full_msg = "8=FIX.4.2" + msg
                        parsed = fix_engine.parse_message(full_msg)
                        if parsed.get('35') == '8' and parsed.get('11') == cl_ord_id:
                            tags = parsed
                            break
            
            if not tags:
                # Fallback to parsing entire response
                tags = fix_engine.parse_message(exec_report)
            
            order_id = tags.get('37', 'Unknown')
            status = tags.get('39', '0')
            
            status_map = {
                '0': 'New',
                '1': 'Partially Filled',
                '2': 'Filled',
                '4': 'Canceled',
                '8': 'Rejected'
            }
            
            # Send logout
            logout = fix_engine.create_logout()
            client.sendall(logout.encode('utf-8'))
            
            return jsonify({
                'success': True,
                'order_id': order_id,
                'cl_ord_id': cl_ord_id,
                'status': status_map.get(status, 'Unknown'),
                'message': 'Order submitted successfully'
            })
            
        finally:
            client.close()
            
    except socket.timeout:
        logger.error("Timeout connecting to exchange")
        return jsonify({'error': 'Exchange connection timeout'}), 504
    except ConnectionRefusedError:
        logger.error("Exchange server not available")
        return jsonify({'error': 'Exchange server not available'}), 503
    except Exception as e:
        logger.error(f"Error submitting order: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
