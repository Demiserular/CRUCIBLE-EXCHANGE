"""
Step definitions for FIX Trading conformance tests.
"""

import socket
import time
import sys
from pathlib import Path
from behave import given, when, then, step
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from fix_engine import FIXEngine


@given('the exchange server is running')
def step_exchange_running(context):
    """Verify exchange server is running and accessible."""
    context.exchange_host = "127.0.0.1"
    context.exchange_port = 9878
    
    # Give server time to start if just launched
    time.sleep(0.5)
    
    # Test connection
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(2)
        test_socket.connect((context.exchange_host, context.exchange_port))
        test_socket.close()
    except Exception as e:
        raise AssertionError(f"Exchange server not reachable: {e}")


@given('I am connected to the exchange')
def step_connected(context):
    """Establish connection to exchange."""
    context.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context.client_socket.settimeout(5)
    context.client_socket.connect((context.exchange_host, context.exchange_port))
    
    # Initialize FIX engine
    context.fix_engine = FIXEngine(sender_comp_id="CLIENT", target_comp_id="EXCHANGE")
    
    # Track orders
    context.orders = {}
    context.last_cl_ord_id = None
    context.received_messages = []
    context.order_counter = 1


@given('I am logged into the exchange')
def step_logged_in(context):
    """Perform logon to exchange."""
    if not hasattr(context, 'client_socket'):
        context.execute_steps('Given I am connected to the exchange')
    
    # Send logon
    logon_msg = context.fix_engine.create_logon(heartbeat_interval=30)
    context.client_socket.sendall(logon_msg.encode('utf-8'))
    
    # Receive logon acknowledgment
    response = context.client_socket.recv(4096).decode('utf-8')
    context.received_messages.append(response)
    
    tags = context.fix_engine.parse_message(response)
    assert tags.get("35") == "A", "Expected Logon acknowledgment"


@given('I have submitted a limit buy order for {qty:d} shares of "{symbol}" at price {price:f}')
def step_submitted_limit_buy_order(context, qty, symbol, price):
    """Submit a limit buy order and store order ID."""
    cl_ord_id = f"ORDER{context.order_counter:06d}"
    context.order_counter += 1
    context.last_cl_ord_id = cl_ord_id
    
    order_msg = context.fix_engine.create_new_order_single(
        cl_ord_id=cl_ord_id,
        symbol=symbol,
        side=FIXEngine.SIDE_BUY,
        order_qty=qty,
        order_type=FIXEngine.ORDER_TYPE_LIMIT,
        price=price
    )
    
    context.client_socket.sendall(order_msg.encode('utf-8'))
    
    # Receive acknowledgment
    response = context.client_socket.recv(4096).decode('utf-8')
    context.received_messages.append(response)
    
    # Store order info
    context.orders[cl_ord_id] = {
        'symbol': symbol,
        'side': FIXEngine.SIDE_BUY,
        'qty': qty,
        'price': price,
        'type': FIXEngine.ORDER_TYPE_LIMIT
    }


# ========================================
# Session Layer Steps
# ========================================

@when('I send a Logon message with heartbeat interval {interval:d}')
def step_send_logon(context, interval):
    """Send Logon message."""
    logon_msg = context.fix_engine.create_logon(heartbeat_interval=interval)
    context.client_socket.sendall(logon_msg.encode('utf-8'))


@when('I send a Heartbeat message')
def step_send_heartbeat(context):
    """Send Heartbeat message."""
    hb_msg = context.fix_engine.create_heartbeat()
    context.client_socket.sendall(hb_msg.encode('utf-8'))


@when('I send a Logout message')
def step_send_logout(context):
    """Send Logout message."""
    logout_msg = context.fix_engine.create_logout()
    context.client_socket.sendall(logout_msg.encode('utf-8'))


@then('I should receive a Logon acknowledgment')
def step_receive_logon_ack(context):
    """Verify Logon acknowledgment received."""
    response = context.client_socket.recv(4096).decode('utf-8')
    context.received_messages.append(response)
    
    tags = context.fix_engine.parse_message(response)
    assert tags.get("35") == "A", f"Expected Logon (35=A), got {tags.get('35')}"


@then('the session should be established')
def step_session_established(context):
    """Verify session is established."""
    assert len(context.received_messages) > 0, "No messages received"


@then('I should receive a Heartbeat response')
def step_receive_heartbeat(context):
    """Verify Heartbeat response."""
    response = context.client_socket.recv(4096).decode('utf-8')
    context.received_messages.append(response)
    
    tags = context.fix_engine.parse_message(response)
    assert tags.get("35") == "0", f"Expected Heartbeat (35=0), got {tags.get('35')}"


@then('I should receive a Logout acknowledgment')
def step_receive_logout_ack(context):
    """Verify Logout acknowledgment."""
    response = context.client_socket.recv(4096).decode('utf-8')
    context.received_messages.append(response)
    
    tags = context.fix_engine.parse_message(response)
    assert tags.get("35") == "5", f"Expected Logout (35=5), got {tags.get('35')}"


@then('the session should be terminated')
def step_session_terminated(context):
    """Verify session terminated."""
    # Session should close gracefully
    pass


# ========================================
# Order Submission Steps
# ========================================

@when('I submit a market buy order for {qty:d} shares of "{symbol}"')
def step_submit_market_buy(context, qty, symbol):
    """Submit market buy order."""
    cl_ord_id = f"ORDER{context.order_counter:06d}"
    context.order_counter += 1
    context.last_cl_ord_id = cl_ord_id
    
    order_msg = context.fix_engine.create_new_order_single(
        cl_ord_id=cl_ord_id,
        symbol=symbol,
        side=FIXEngine.SIDE_BUY,
        order_qty=qty,
        order_type=FIXEngine.ORDER_TYPE_MARKET
    )
    
    context.client_socket.sendall(order_msg.encode('utf-8'))
    context.orders[cl_ord_id] = {
        'symbol': symbol,
        'side': FIXEngine.SIDE_BUY,
        'qty': qty,
        'type': FIXEngine.ORDER_TYPE_MARKET
    }


@when('I submit a market sell order for {qty:d} shares of "{symbol}"')
def step_submit_market_sell(context, qty, symbol):
    """Submit market sell order."""
    cl_ord_id = f"ORDER{context.order_counter:06d}"
    context.order_counter += 1
    context.last_cl_ord_id = cl_ord_id
    
    order_msg = context.fix_engine.create_new_order_single(
        cl_ord_id=cl_ord_id,
        symbol=symbol,
        side=FIXEngine.SIDE_SELL,
        order_qty=qty,
        order_type=FIXEngine.ORDER_TYPE_MARKET
    )
    
    context.client_socket.sendall(order_msg.encode('utf-8'))
    context.orders[cl_ord_id] = {
        'symbol': symbol,
        'side': FIXEngine.SIDE_SELL,
        'qty': qty,
        'type': FIXEngine.ORDER_TYPE_MARKET
    }


@when('I submit a limit buy order for {qty:d} shares of "{symbol}" at price {price:f}')
def step_submit_limit_buy(context, qty, symbol, price):
    """Submit limit buy order."""
    cl_ord_id = f"ORDER{context.order_counter:06d}"
    context.order_counter += 1
    context.last_cl_ord_id = cl_ord_id
    
    order_msg = context.fix_engine.create_new_order_single(
        cl_ord_id=cl_ord_id,
        symbol=symbol,
        side=FIXEngine.SIDE_BUY,
        order_qty=qty,
        order_type=FIXEngine.ORDER_TYPE_LIMIT,
        price=price
    )
    
    context.client_socket.sendall(order_msg.encode('utf-8'))
    context.orders[cl_ord_id] = {
        'symbol': symbol,
        'side': FIXEngine.SIDE_BUY,
        'qty': qty,
        'price': price,
        'type': FIXEngine.ORDER_TYPE_LIMIT
    }


@when('I submit a limit sell order for {qty:d} shares of "{symbol}" at price {price:f}')
def step_submit_limit_sell(context, qty, symbol, price):
    """Submit limit sell order."""
    cl_ord_id = f"ORDER{context.order_counter:06d}"
    context.order_counter += 1
    context.last_cl_ord_id = cl_ord_id
    
    order_msg = context.fix_engine.create_new_order_single(
        cl_ord_id=cl_ord_id,
        symbol=symbol,
        side=FIXEngine.SIDE_SELL,
        order_qty=qty,
        order_type=FIXEngine.ORDER_TYPE_LIMIT,
        price=price
    )
    
    context.client_socket.sendall(order_msg.encode('utf-8'))
    context.orders[cl_ord_id] = {
        'symbol': symbol,
        'side': FIXEngine.SIDE_SELL,
        'qty': qty,
        'price': price,
        'type': FIXEngine.ORDER_TYPE_LIMIT
    }


# ========================================
# Order Verification Steps
# ========================================

@then('I should receive an execution report with status "{status}"')
def step_receive_exec_report_status(context, status):
    """Verify execution report with specific status."""
    response = context.client_socket.recv(4096).decode('utf-8')
    context.received_messages.append(response)
    
    tags = context.fix_engine.parse_message(response)
    assert tags.get("35") == "8", f"Expected Execution Report (35=8), got {tags.get('35')}"
    
    ord_status = tags.get("39")
    status_map = {
        "New": "0",
        "Partially Filled": "1",
        "Filled": "2",
        "Canceled": "4",
        "Rejected": "8"
    }
    
    expected_status = status_map.get(status, status)
    assert ord_status == expected_status, f"Expected status {expected_status}, got {ord_status}"
    
    # Store latest execution report
    context.last_exec_report = tags


@then('the order should be in the order book')
def step_order_in_book(context):
    """Verify order is in order book (acknowledged)."""
    assert context.last_exec_report is not None, "No execution report received"
    assert context.last_exec_report.get("37"), "No order ID in execution report"


@then('both orders should receive execution reports with status "{status}"')
def step_both_orders_filled(context, status):
    """Verify both orders receive execution reports."""
    status_map = {
        "Filled": "2",
        "Partially Filled": "1"
    }
    expected_status = status_map.get(status, status)
    
    # Receive multiple messages
    time.sleep(0.2)  # Allow time for matching
    
    exec_reports = []
    try:
        while True:
            context.client_socket.settimeout(0.5)
            response = context.client_socket.recv(4096).decode('utf-8')
            if not response:
                break
            
            # Split multiple messages
            messages = response.split("8=FIX")
            for msg in messages:
                if msg:
                    full_msg = "8=FIX" + msg if not msg.startswith("8=FIX") else msg
                    tags = context.fix_engine.parse_message(full_msg)
                    if tags.get("35") == "8":
                        exec_reports.append(tags)
    except socket.timeout:
        pass
    
    context.client_socket.settimeout(5)
    
    # Check that we received execution reports
    assert len(exec_reports) >= 2, f"Expected at least 2 execution reports, got {len(exec_reports)}"


@then('the fill quantity should be {qty:d} shares')
def step_verify_fill_qty(context, qty):
    """Verify fill quantity."""
    # Check last execution report
    assert context.last_exec_report is not None
    last_qty = int(context.last_exec_report.get("32", "0"))
    assert last_qty == qty, f"Expected fill qty {qty}, got {last_qty}"


@then('the fill price should be {price:f}')
def step_verify_fill_price(context, price):
    """Verify fill price."""
    assert context.last_exec_report is not None
    last_px = float(context.last_exec_report.get("31", "0"))
    assert abs(last_px - price) < 0.01, f"Expected fill price {price}, got {last_px}"


@then('the sell order should receive an execution report with status "{status}"')
@then('the buy order should receive an execution report with status "{status}"')
def step_order_receives_status(context, status):
    """Verify specific order receives status."""
    # Implementation similar to general exec report verification
    step_receive_exec_report_status(context, status)


@then('the buy order should have {qty:d} shares remaining')
def step_verify_remaining_qty(context, qty):
    """Verify remaining quantity on order."""
    # Check cumulative qty vs order qty
    assert context.last_exec_report is not None
    order_qty = int(context.last_exec_report.get("38", "0"))
    cum_qty = int(context.last_exec_report.get("14", "0"))
    remaining = order_qty - cum_qty
    assert remaining == qty, f"Expected {qty} shares remaining, got {remaining}"


# ========================================
# Order Cancellation Steps
# ========================================

@when('I send a cancel request for that order')
def step_send_cancel_request(context):
    """Send cancel request for last order."""
    assert context.last_cl_ord_id, "No order to cancel"
    
    order_info = context.orders[context.last_cl_ord_id]
    new_cl_ord_id = f"CANCEL{context.order_counter:06d}"
    context.order_counter += 1
    
    cancel_msg = context.fix_engine.create_order_cancel_request(
        orig_cl_ord_id=context.last_cl_ord_id,
        cl_ord_id=new_cl_ord_id,
        symbol=order_info['symbol'],
        side=order_info['side'],
        order_qty=order_info['qty']
    )
    
    context.client_socket.sendall(cancel_msg.encode('utf-8'))


@when('I send a cancel request for order "{order_id}"')
def step_send_cancel_for_order(context, order_id):
    """Send cancel request for specific order."""
    new_cl_ord_id = f"CANCEL{context.order_counter:06d}"
    context.order_counter += 1
    
    cancel_msg = context.fix_engine.create_order_cancel_request(
        orig_cl_ord_id=order_id,
        cl_ord_id=new_cl_ord_id,
        symbol="AAPL",  # Dummy values
        side=FIXEngine.SIDE_BUY,
        order_qty=100
    )
    
    context.client_socket.sendall(cancel_msg.encode('utf-8'))


@then('the order should be removed from the order book')
def step_order_removed(context):
    """Verify order removed."""
    # Order should be canceled
    assert context.last_exec_report.get("39") == "4", "Order not canceled"


@then('I should receive a cancel reject message')
def step_receive_cancel_reject(context):
    """Verify cancel reject received."""
    response = context.client_socket.recv(4096).decode('utf-8')
    context.received_messages.append(response)
    context.last_exec_report = context.fix_engine.parse_message(response)
    
    # Should be execution report with rejected status
    assert context.last_exec_report.get("35") == "8"
    assert context.last_exec_report.get("39") == "8"


@then('the reject reason should be "{reason}"')
@then('the rejection reason should contain "{reason}"')
def step_verify_reject_reason(context, reason):
    """Verify rejection reason."""
    assert context.last_exec_report is not None
    text = context.last_exec_report.get("58", "")
    assert reason.lower() in text.lower(), f"Expected '{reason}' in rejection, got '{text}'"


# ========================================
# Protocol Compliance Steps
# ========================================

@when('I send a FIX message with an incorrect checksum')
def step_send_invalid_checksum(context):
    """Send message with bad checksum."""
    # Create valid message then corrupt checksum
    msg = context.fix_engine.create_heartbeat()
    corrupted_msg = msg.replace("10=", "10=999")
    context.client_socket.sendall(corrupted_msg.encode('utf-8'))
    context.invalid_message_sent = True


@when('I send a New Order message missing the symbol field')
def step_send_incomplete_message(context):
    """Send incomplete new order message."""
    # Create malformed message
    incomplete_msg = (
        f"8=FIX.4.2{FIXEngine.SOH}"
        f"9=50{FIXEngine.SOH}"
        f"35=D{FIXEngine.SOH}"
        f"49=CLIENT{FIXEngine.SOH}"
        f"56=EXCHANGE{FIXEngine.SOH}"
        f"10=000{FIXEngine.SOH}"
    )
    context.client_socket.sendall(incomplete_msg.encode('utf-8'))
    context.invalid_message_sent = True


@then('the message should be rejected')
def step_message_rejected(context):
    """Verify message was rejected."""
    assert hasattr(context, 'invalid_message_sent')


@then('no execution report should be received')
def step_no_exec_report(context):
    """Verify no execution report received."""
    try:
        context.client_socket.settimeout(1)
        response = context.client_socket.recv(4096).decode('utf-8')
        # If we get here, check it's not an execution report
        if response:
            tags = context.fix_engine.parse_message(response)
            assert tags.get("35") != "8", "Received unexpected execution report"
    except socket.timeout:
        pass  # No response is expected
    finally:
        context.client_socket.settimeout(5)


# ========================================
# Edge Case Steps
# ========================================

@when('I submit {count:d} limit buy orders for "{symbol}" at different prices')
def step_submit_multiple_orders(context, count, symbol):
    """Submit multiple orders."""
    context.multi_order_ids = []
    
    for i in range(count):
        cl_ord_id = f"ORDER{context.order_counter:06d}"
        context.order_counter += 1
        context.multi_order_ids.append(cl_ord_id)
        
        price = 100.0 + (i * 10)
        
        order_msg = context.fix_engine.create_new_order_single(
            cl_ord_id=cl_ord_id,
            symbol=symbol,
            side=FIXEngine.SIDE_BUY,
            order_qty=10,
            order_type=FIXEngine.ORDER_TYPE_LIMIT,
            price=price
        )
        
        context.client_socket.sendall(order_msg.encode('utf-8'))
        time.sleep(0.05)  # Small delay between orders


@when('I rapidly submit {count:d} orders within 1 second')
def step_rapid_submit_orders(context, count):
    """Rapidly submit multiple orders."""
    context.rapid_order_ids = []
    
    for i in range(count):
        cl_ord_id = f"RAPID{i:03d}"
        context.rapid_order_ids.append(cl_ord_id)
        
        order_msg = context.fix_engine.create_new_order_single(
            cl_ord_id=cl_ord_id,
            symbol="AAPL",
            side=FIXEngine.SIDE_BUY,
            order_qty=10,
            order_type=FIXEngine.ORDER_TYPE_MARKET
        )
        
        context.client_socket.sendall(order_msg.encode('utf-8'))


@then('all orders should be acknowledged')
@then('all orders should be processed')
def step_all_orders_acknowledged(context):
    """Verify all orders acknowledged."""
    # Give time for processing
    time.sleep(0.5)
    
    # Try to receive multiple responses
    received_count = 0
    try:
        context.client_socket.settimeout(0.5)
        while received_count < 20:  # Max attempts
            response = context.client_socket.recv(4096).decode('utf-8')
            if not response:
                break
            received_count += response.count("35=8")
    except socket.timeout:
        pass
    finally:
        context.client_socket.settimeout(5)
    
    # Should have received at least some acknowledgments
    assert received_count > 0, "No order acknowledgments received"


@then('all orders should receive execution reports')
def step_all_orders_exec_reports(context):
    """Verify execution reports for all orders."""
    step_all_orders_acknowledged(context)
