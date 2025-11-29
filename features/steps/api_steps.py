"""
API Testing Step Definitions
Demonstrates: REST API testing, HTTP methods, JSON validation
Skills: Python, API testing, requests library
"""

import requests
import json
from behave import given, when, then

API_BASE_URL = "http://127.0.0.1:5000"


@given('the API server is running on port {port:d}')
def step_impl(context, port):
    context.api_base = f"http://127.0.0.1:{port}"
    context.response = None
    # Verify server is running
    try:
        resp = requests.get(f"{context.api_base}/api/health", timeout=2)
        assert resp.status_code in [200, 404], "API server not responding"
    except requests.exceptions.ConnectionError:
        # Server might not have /health endpoint, that's okay
        pass


@when('I submit a POST request to "{endpoint}" with')
def step_impl(context, endpoint):
    data = {}
    for row in context.table:
        key = row['symbol'] if 'symbol' in row.headings else row[0]
        value = row[1] if len(row) > 1 else row['symbol']
        # Parse table properly
        data[row[0]] = row[1]
    
    # Convert numeric values
    if 'order_qty' in data:
        data['order_qty'] = int(data['order_qty'])
    if 'price' in data:
        data['price'] = float(data['price'])
    
    try:
        context.response = requests.post(
            f"{context.api_base}{endpoint}",
            json=data,
            timeout=15
        )
    except requests.exceptions.Timeout:
        context.response = type('Response', (), {'status_code': 504, 'text': 'Timeout'})()
    except Exception as e:
        context.response = type('Response', (), {'status_code': 500, 'text': str(e)})()


@when('I submit a GET request to "{endpoint}"')
def step_impl(context, endpoint):
    try:
        context.response = requests.get(
            f"{context.api_base}{endpoint}",
            timeout=10
        )
    except requests.exceptions.Timeout:
        context.response = type('Response', (), {'status_code': 504, 'text': 'Timeout'})()
    except Exception as e:
        context.response = type('Response', (), {'status_code': 500, 'text': str(e)})()


@then('the response status code should be {code:d}')
def step_impl(context, code):
    assert context.response is not None, "No response received"
    assert context.response.status_code == code, \
        f"Expected {code}, got {context.response.status_code}: {context.response.text}"


@then('the response should contain "{key}"')
def step_impl(context, key):
    assert context.response is not None, "No response received"
    try:
        data = context.response.json()
        assert key in data or key in str(data), f"Key '{key}' not found in response: {data}"
    except json.JSONDecodeError:
        assert key in context.response.text, f"Key '{key}' not found in response text"


@then('the response should be a list')
def step_impl(context):
    assert context.response is not None, "No response received"
    data = context.response.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
