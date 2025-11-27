# Crucible FIX Exchange - REST API Documentation

## Overview

The Crucible REST API provides HTTP endpoints for interacting with the FIX exchange, querying market data, and submitting manual orders. This API is ideal for building trading dashboards, monitoring tools, and manual trading interfaces.

**Base URL:** `http://127.0.0.1:5000`

---

## Starting the API Server

### Automatic Startup (Recommended)
```bash
# Windows
start_all.bat

# Linux/macOS
./start_all.sh
```

### Manual Startup
```bash
# Activate virtual environment
# Windows: venv\Scripts\activate.bat
# Linux/macOS: source venv/bin/activate

# Start API server
python src/api_server.py
```

The API server will start on port 5000.

---

## Authentication

Currently, the API does not require authentication. In a production environment, you should implement:
- API key authentication
- OAuth 2.0
- JWT tokens
- IP whitelisting

---

## Endpoints

### 1. Health Check

**GET** `/api/health`

Check if the API server and database are operational.

#### Response
```json
{
  "status": "ok",
  "database": "connected"
}
```

#### Example
```bash
curl http://127.0.0.1:5000/api/health
```

---

### 2. Get Order Book

**GET** `/api/orderbook`

Retrieve the current order book with all open buy and sell orders grouped by symbol.

#### Response
```json
{
  "buy_orders": {
    "AAPL": [
      {
        "order_id": "ORD000001",
        "cl_ord_id": "CLIENT001",
        "symbol": "AAPL",
        "side": "Buy",
        "order_qty": 100,
        "order_type": "Limit",
        "price": 150.00,
        "filled_qty": 0,
        "remaining_qty": 100,
        "status": "New",
        "timestamp": "14:30:25"
      }
    ],
    "GOOGL": [...]
  },
  "sell_orders": {
    "AAPL": [...],
    "GOOGL": [...]
  }
}
```

#### Example
```bash
curl http://127.0.0.1:5000/api/orderbook
```

---

### 3. Get Open Orders

**GET** `/api/orders`

Retrieve all currently open orders, optionally filtered by symbol.

#### Query Parameters
| Parameter | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| symbol    | string | No       | Filter orders by symbol (e.g., "AAPL") |

#### Response
```json
{
  "orders": [
    {
      "order_id": "ORD000001",
      "cl_ord_id": "CLIENT001",
      "symbol": "AAPL",
      "side": "1",
      "order_qty": 100,
      "order_type": "2",
      "price": 150.00,
      "filled_qty": 0,
      "remaining_qty": 100,
      "status": "0",
      "timestamp": "14:30:25"
    }
  ],
  "count": 1
}
```

#### Examples
```bash
# Get all orders
curl http://127.0.0.1:5000/api/orders

# Get orders for specific symbol
curl http://127.0.0.1:5000/api/orders?symbol=AAPL
```

---

### 4. Get Recent Executions

**GET** `/api/executions`

Retrieve recent trade executions.

#### Query Parameters
| Parameter | Type    | Required | Description                           |
|-----------|---------|----------|---------------------------------------|
| limit     | integer | No       | Number of executions to return (default: 100, max: 1000) |

#### Response
```json
{
  "executions": [
    {
      "symbol": "AAPL",
      "side": "Buy",
      "last_qty": 100,
      "last_px": 150.00,
      "status": "Filled",
      "timestamp": "14:35:12"
    }
  ],
  "count": 1
}
```

#### Examples
```bash
# Get last 100 executions
curl http://127.0.0.1:5000/api/executions

# Get last 10 executions
curl "http://127.0.0.1:5000/api/executions?limit=10"
```

---

### 5. Get Statistics

**GET** `/api/statistics`

Retrieve exchange statistics including order counts, execution volumes, and trading activity.

#### Response
```json
{
  "total_orders": 156,
  "open_orders": 23,
  "filled_orders": 89,
  "canceled_orders": 44,
  "total_executions": 89,
  "total_volume": 15600,
  "symbols_traded": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
}
```

#### Example
```bash
curl http://127.0.0.1:5000/api/statistics
```

---

### 6. Submit Order

**POST** `/api/submit_order`

Submit a manual order to the exchange via the REST API.

#### Request Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "symbol": "AAPL",
  "side": "1",
  "order_qty": 100,
  "order_type": "2",
  "price": 150.00
}
```

#### Parameters
| Parameter  | Type    | Required | Description                                           |
|------------|---------|----------|-------------------------------------------------------|
| symbol     | string  | Yes      | Trading symbol (AAPL, GOOGL, MSFT, AMZN, TSLA)       |
| side       | string  | Yes      | Order side: "1" = Buy, "2" = Sell                    |
| order_qty  | integer | Yes      | Order quantity (must be positive)                     |
| order_type | string  | Yes      | Order type: "1" = Market, "2" = Limit                |
| price      | float   | No*      | Limit price (*Required for limit orders)             |

#### Response (Success)
```json
{
  "success": true,
  "order_id": "ORD000042",
  "cl_ord_id": "MAN00001234",
  "status": "New",
  "message": "Order submitted successfully"
}
```

#### Response (Error)
```json
{
  "error": "Invalid symbol: INVALID"
}
```

#### Status Codes
| Code | Description                          |
|------|--------------------------------------|
| 200  | Order submitted successfully         |
| 400  | Bad request (invalid parameters)     |
| 503  | Exchange server not available        |
| 504  | Exchange connection timeout          |

#### Examples

**Market Buy Order:**
```bash
curl -X POST http://127.0.0.1:5000/api/submit_order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "side": "1",
    "order_qty": 100,
    "order_type": "1"
  }'
```

**Limit Sell Order:**
```bash
curl -X POST http://127.0.0.1:5000/api/submit_order \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "GOOGL",
    "side": "2",
    "order_qty": 50,
    "order_type": "2",
    "price": 140.00
  }'
```

**Using Python:**
```python
import requests

order = {
    "symbol": "AAPL",
    "side": "1",
    "order_qty": 100,
    "order_type": "2",
    "price": 150.00
}

response = requests.post(
    "http://127.0.0.1:5000/api/submit_order",
    json=order
)

print(response.json())
```

**Using JavaScript:**
```javascript
fetch('http://127.0.0.1:5000/api/submit_order', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    symbol: 'AAPL',
    side: '1',
    order_qty: 100,
    order_type: '2',
    price: 150.00
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Error Handling

All endpoints return appropriate HTTP status codes and error messages.

### Common Error Responses

**400 Bad Request:**
```json
{
  "error": "Missing required field: symbol"
}
```

**503 Service Unavailable:**
```json
{
  "error": "Database not available"
}
```

**504 Gateway Timeout:**
```json
{
  "error": "Exchange connection timeout"
}
```

---

## CORS Support

The API supports Cross-Origin Resource Sharing (CORS) and accepts requests from any origin. This allows web dashboards to call the API directly from the browser.

Supported methods: `GET`, `POST`, `OPTIONS`

---

## Rate Limiting

Currently, there is no rate limiting. For production use, implement rate limiting to prevent abuse:
- Per IP address
- Per API key
- Per endpoint

---

## Best Practices

### 1. Error Handling
Always check the HTTP status code and handle errors gracefully:
```python
response = requests.post(url, json=order)
if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f"Order placed: {data['order_id']}")
    else:
        print(f"Order failed: {data.get('error')}")
else:
    print(f"HTTP Error: {response.status_code}")
```

### 2. Timeouts
Set appropriate timeouts for API calls:
```python
response = requests.get(url, timeout=10)
```

### 3. Retries
Implement retry logic for transient failures:
```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
```

### 4. Connection Pooling
Reuse sessions for multiple requests:
```python
session = requests.Session()
response1 = session.get(url1)
response2 = session.get(url2)
```

---

## Integration Examples

### Python Trading Bot
```python
import requests
import time

API_BASE = "http://127.0.0.1:5000/api"

def get_orderbook():
    response = requests.get(f"{API_BASE}/orderbook")
    return response.json()

def submit_order(symbol, side, qty, order_type, price=None):
    order = {
        "symbol": symbol,
        "side": side,
        "order_qty": qty,
        "order_type": order_type
    }
    if price:
        order["price"] = price
    
    response = requests.post(f"{API_BASE}/submit_order", json=order)
    return response.json()

# Example: Submit limit buy order
result = submit_order("AAPL", "1", 100, "2", 150.00)
print(f"Order placed: {result}")

# Example: Get order book
orderbook = get_orderbook()
print(f"Buy orders: {len(orderbook['buy_orders'])}")
```

### Node.js Integration
```javascript
const axios = require('axios');

const API_BASE = 'http://127.0.0.1:5000/api';

async function submitOrder(symbol, side, qty, orderType, price) {
  const order = {
    symbol,
    side,
    order_qty: qty,
    order_type: orderType,
    ...(price && { price })
  };
  
  try {
    const response = await axios.post(`${API_BASE}/submit_order`, order);
    return response.data;
  } catch (error) {
    console.error('Order failed:', error.response.data);
    throw error;
  }
}

// Example usage
submitOrder('AAPL', '1', 100, '2', 150.00)
  .then(result => console.log('Order placed:', result));
```

---

## Monitoring

### Health Check Monitoring
Set up periodic health checks to ensure the API is responsive:

```bash
#!/bin/bash
# health_check.sh
while true; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/api/health)
  if [ "$STATUS" -eq 200 ]; then
    echo "$(date): API is healthy"
  else
    echo "$(date): API is down (HTTP $STATUS)"
    # Send alert
  fi
  sleep 60
done
```

---

## Troubleshooting

### API Server Not Starting
1. Check if port 5000 is already in use:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   
   # Linux/macOS
   lsof -i :5000
   ```

2. Check exchange server is running (port 9878)

3. Check database file exists: `crucible.db`

### Connection Refused
- Ensure exchange server is running first
- Verify firewall settings
- Check server logs

### Slow Response Times
- Check database performance
- Monitor server resources
- Consider enabling caching

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Implement authentication/authorization
- [ ] Add rate limiting
- [ ] Enable HTTPS/TLS
- [ ] Configure proper CORS settings
- [ ] Set up monitoring and alerting
- [ ] Implement request logging
- [ ] Add input sanitization
- [ ] Configure error tracking (e.g., Sentry)
- [ ] Set up load balancing
- [ ] Implement database connection pooling
- [ ] Add API versioning (e.g., `/api/v1/`)
- [ ] Document all endpoints with OpenAPI/Swagger

---

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review README.md
- Consult TEST_RESULTS_SUMMARY.md

---

**Last Updated:** 2024-11-21  
**API Version:** 1.0.0  
**Compatible with:** Crucible FIX Exchange v1.0.0
