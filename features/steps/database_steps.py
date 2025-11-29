"""
Database Testing Step Definitions
Demonstrates: SQL knowledge, database testing, data integrity validation
Skills: Python, SQLite, SQL queries, concurrent operations
"""

import os
import sys
import threading
import time
from behave import given, when, then

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from database_sqlite import DatabaseManager

TEST_DB_PATH = "test_db_features.db"


@given('a test database connection is established')
def step_impl(context):
    # Clean up existing test DB
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    context.db = DatabaseManager(TEST_DB_PATH)
    context.test_orders = []


@when('I save an order with')
def step_impl(context):
    order_data = {}
    for row in context.table:
        key = row[0]
        value = row[1]
        # Type conversion
        if key in ['order_qty']:
            value = int(value)
        elif key in ['price']:
            value = float(value)
        order_data[key] = value
    
    # Add timestamp if not present
    if 'timestamp' not in order_data:
        order_data['timestamp'] = time.strftime('%H:%M:%S')
    
    context.db.save_order(order_data)
    context.last_order_id = order_data.get('order_id')


@then('I should be able to retrieve the order by id "{order_id}"')
def step_impl(context, order_id):
    orders = context.db.get_orders()
    found = any(o.get('order_id') == order_id for o in orders)
    assert found, f"Order {order_id} not found in database"
    context.retrieved_order = next(o for o in orders if o.get('order_id') == order_id)


@then('the retrieved order should have symbol "{symbol}"')
def step_impl(context, symbol):
    assert context.retrieved_order.get('symbol') == symbol, \
        f"Expected symbol {symbol}, got {context.retrieved_order.get('symbol')}"


@when('I save an execution with')
def step_impl(context):
    exec_data = {}
    for row in context.table:
        key = row[0]
        value = row[1]
        if key in ['last_qty']:
            value = int(value)
        elif key in ['last_px']:
            value = float(value)
        exec_data[key] = value
    
    if 'timestamp' not in exec_data:
        exec_data['timestamp'] = time.strftime('%H:%M:%S')
    
    context.db.save_execution(exec_data)


@then('I should be able to retrieve executions for order "{order_id}"')
def step_impl(context, order_id):
    executions = context.db.get_executions()
    found = any(e.get('order_id') == order_id for e in executions)
    assert found, f"No executions found for order {order_id}"


@given('multiple test orders exist in the database')
def step_impl(context):
    test_orders = [
        {'order_id': 'MULTI001', 'symbol': 'AAPL', 'side': 'Buy', 'order_qty': 100, 'price': 150.0, 'status': 'New', 'timestamp': '10:00:00'},
        {'order_id': 'MULTI002', 'symbol': 'AAPL', 'side': 'Sell', 'order_qty': 50, 'price': 151.0, 'status': 'Filled', 'timestamp': '10:00:01'},
        {'order_id': 'MULTI003', 'symbol': 'GOOGL', 'side': 'Buy', 'order_qty': 200, 'price': 175.0, 'status': 'New', 'timestamp': '10:00:02'},
        {'order_id': 'MULTI004', 'symbol': 'MSFT', 'side': 'Sell', 'order_qty': 75, 'price': 380.0, 'status': 'Canceled', 'timestamp': '10:00:03'},
    ]
    
    for order in test_orders:
        context.db.save_order(order)
    
    context.test_orders = test_orders


@when('I query orders with status "{status}"')
def step_impl(context, status):
    all_orders = context.db.get_orders()
    context.queried_orders = [o for o in all_orders if o.get('status') == status]


@then('I should receive a non-empty list of orders')
def step_impl(context):
    assert len(context.queried_orders) > 0, "Expected non-empty list of orders"


@when('I query orders for symbol "{symbol}"')
def step_impl(context, symbol):
    all_orders = context.db.get_orders()
    context.queried_orders = [o for o in all_orders if o.get('symbol') == symbol]


@then('I should receive orders only for symbol "{symbol}"')
def step_impl(context, symbol):
    for order in context.queried_orders:
        assert order.get('symbol') == symbol, f"Found order with wrong symbol: {order.get('symbol')}"


@when('I query the total order count')
def step_impl(context):
    orders = context.db.get_orders()
    context.order_count = len(orders)


@then('the count should be greater than {count:d}')
def step_impl(context, count):
    assert context.order_count > count, f"Expected count > {count}, got {context.order_count}"


@when('I save {count:d} orders concurrently')
def step_impl(context, count):
    context.concurrent_results = []
    threads = []
    
    def save_order(idx):
        try:
            order = {
                'order_id': f'CONCURRENT_{idx}',
                'symbol': 'AAPL',
                'side': 'Buy',
                'order_qty': 100,
                'price': 150.0,
                'status': 'New',
                'timestamp': time.strftime('%H:%M:%S')
            }
            context.db.save_order(order)
            context.concurrent_results.append(True)
        except Exception as e:
            context.concurrent_results.append(False)
    
    for i in range(count):
        t = threading.Thread(target=save_order, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()


@then('all {count:d} orders should be persisted successfully')
def step_impl(context, count):
    assert len(context.concurrent_results) == count, f"Expected {count} results, got {len(context.concurrent_results)}"
    assert all(context.concurrent_results), "Some concurrent writes failed"
    
    # Verify in database
    orders = context.db.get_orders()
    concurrent_orders = [o for o in orders if o.get('order_id', '').startswith('CONCURRENT_')]
    assert len(concurrent_orders) >= count, f"Expected {count} concurrent orders, found {len(concurrent_orders)}"


def after_feature(context, feature):
    """Cleanup after database testing feature."""
    if hasattr(context, 'db'):
        context.db.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
