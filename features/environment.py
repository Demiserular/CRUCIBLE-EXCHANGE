
import threading
import time
import os
import sys
import logging
from behave import fixture, use_fixture

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from exchange_server import ExchangeServer
from database_sqlite import DatabaseManager

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("behave_test")

TEST_DB = "test_crucible.db"
TEST_HOST = "127.0.0.1"
TEST_PORT = 9879

# Live server details
LIVE_HOST = "127.0.0.1"
LIVE_PORT = 9878

@fixture
def start_exchange_server(context):
    """Fixture to start and stop the exchange server."""
    
    # Check if we should use the live server
    if os.environ.get('USE_LIVE_SERVER') == 'true':
        logger.info("Using LIVE Exchange Server")
        context.host = LIVE_HOST
        context.port = LIVE_PORT
        # We don't manage the server or DB in this case
        yield None
        return

    # Remove existing test DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Initialize DB manager
    context.db_manager = DatabaseManager(TEST_DB)
    
    # Initialize Server
    context.server = ExchangeServer(host=TEST_HOST, port=TEST_PORT, db_manager=context.db_manager)
    
    # Start server in a thread
    server_thread = threading.Thread(target=context.server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(1)
    logger.info("Test Exchange Server started")
    
    context.host = TEST_HOST
    context.port = TEST_PORT
    
    yield context.server
    
    # Cleanup
    context.server.stop()
    server_thread.join(timeout=2)
    context.db_manager.close()
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    logger.info("Test Exchange Server stopped and DB cleaned")

def before_all(context):
    use_fixture(start_exchange_server, context)

def after_scenario(context, scenario):
    # Stop listener thread if running
    if hasattr(context, 'listening'):
        context.listening = False
        if hasattr(context, 'listener_thread'):
            context.listener_thread.join(timeout=1.0)

    # Optional: Clear order book between scenarios if needed
    # But for now we might want to keep state or reset it.
    # A simple way to reset is to clear the internal dicts
    if hasattr(context, 'server') and context.server:
        with context.server.order_book.lock:
            context.server.order_book.orders.clear()
            context.server.order_book.buy_orders.clear()
            context.server.order_book.sell_orders.clear()
            context.server.order_book.executions.clear()
