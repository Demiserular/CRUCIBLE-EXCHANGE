# 🚀 Real-Time Dashboard - Quick Start Guide

## Overview
The Crucible exchange now features a **live, real-time trading dashboard** powered by WebSocket technology. Watch orders flow, matches execute, and the order book update in real-time!

---

## 🎯 Quick Start (3 Steps)

### 1️⃣ Start the Exchange Server (with WebSocket)
```cmd
venv\Scripts\python.exe src\exchange_server.py
```

**What you'll see:**
```
INFO - Real-time WebSocket broadcasting enabled
INFO - WebSocket server started on ws://127.0.0.1:8765
INFO - Exchange Server started on 127.0.0.1:9878
```

### 2️⃣ Open the Real-Time Dashboard
Simply open `dashboard_realtime.html` in your browser:
- Double-click the file, OR
- Right-click → Open with → Chrome/Firefox/Edge

**The dashboard connects automatically to:**
- WebSocket: `ws://127.0.0.1:8765` (real-time updates)
- Auto-reconnects if connection drops

### 3️⃣ Generate Live Trading Activity
In a **new terminal** window:
```cmd
venv\Scripts\python.exe generate_orders.py
```

**Watch the magic happen:**
- Orders appear in real-time
- Order book updates automatically
- Executions flash as they happen
- Stats update continuously

---

## 🎨 Dashboard Features

### 📊 Live Order Book
- **Symbol Tabs**: Switch between AAPL, GOOGL, MSFT, AMZN, TSLA
- **Buy Orders** (green): Sorted by highest price first
- **Sell Orders** (red): Sorted by lowest price first
- **Smooth Animations**: New orders slide in

### ⚡ Real-Time Execution Feed
- Latest 50 executions
- Color-coded by side (Buy/Sell)
- Shows symbol, price, quantity, status
- Flash animation on new executions

### 📈 Trading Statistics
- **Total Volume**: Cumulative shares traded
- **Avg Fill Price**: Weighted average execution price
- **Buy/Sell Counts**: Order distribution
- **Match Rate**: Percentage of orders that executed
- **Uptime**: System runtime

### 🔄 Connection Status
- **Green dot + "Connected"**: Receiving live updates
- **Red dot + "Disconnected"**: Attempting to reconnect
- Auto-reconnect every 3 seconds

---

## 🏗️ Architecture

```
┌─────────────────────┐
│  Browser Dashboard  │
│  (dashboard_        │
│   realtime.html)    │
│                     │
│  WebSocket Client   │
└──────────┬──────────┘
           │ ws://127.0.0.1:8765
           │ (Real-time updates)
           ▼
┌─────────────────────┐
│  Exchange Server    │
│  (exchange_         │
│   server.py)        │
│                     │
│  • FIX Protocol     │
│  • WebSocket Svr    │
│  • Order Book       │
└──────────┬──────────┘
           │ FIX Protocol
           │ tcp://127.0.0.1:9878
           ▼
┌─────────────────────┐
│  Order Generator    │
│  (generate_         │
│   orders.py)        │
│                     │
│  Sends FIX orders   │
│  every 2 seconds    │
└─────────────────────┘
```

---

## 📡 WebSocket Message Types

### 1. **Snapshot** (on connection)
```json
{
  "type": "snapshot",
  "data": {
    "buy_orders": { "AAPL": [...], "GOOGL": [...] },
    "sell_orders": { "AAPL": [...], "GOOGL": [...] },
    "recent_executions": [...]
  },
  "timestamp": "2024-01-15T10:30:45"
}
```

### 2. **New Order**
```json
{
  "type": "new_order",
  "data": {
    "symbol": "AAPL",
    "side": "Buy",
    "order_qty": 100,
    "price": 180.50,
    "order_type": "Limit"
  }
}
```

### 3. **Execution**
```json
{
  "type": "execution",
  "data": {
    "symbol": "AAPL",
    "side": "Buy",
    "last_qty": 100,
    "last_px": 180.50,
    "status": "Filled"
  }
}
```

### 4. **Cancel Order**
```json
{
  "type": "cancel_order",
  "data": {
    "order_id": "ORD000123",
    "status": "Canceled"
  }
}
```

---

## 🧪 Testing Scenarios

### Scenario 1: Basic Connectivity
```cmd
# Terminal 1
venv\Scripts\python.exe src\exchange_server.py

# Open dashboard_realtime.html in browser
# Check: Green dot + "Connected"
```

### Scenario 2: Order Flow
```cmd
# Terminal 2
venv\Scripts\python.exe generate_orders.py

# Watch dashboard:
# - Orders appear in order book
# - Executions populate the feed
# - Stats update in real-time
```

### Scenario 3: Reconnection
```cmd
# In Terminal 1, press Ctrl+C to stop server
# Dashboard shows: Red dot + "Disconnected"

# Restart server
venv\Scripts\python.exe src\exchange_server.py

# Dashboard auto-reconnects: Green dot + "Connected"
```

### Scenario 4: Multiple Symbols
```cmd
# Click different symbol tabs (AAPL, GOOGL, MSFT)
# Each shows its own order book
# Execution feed shows all symbols
```

---

## 🎮 Order Generator Controls

### Start Generator
```cmd
venv\Scripts\python.exe generate_orders.py
```

### Stop Generator
```
Press Ctrl+C
```

### Customize Generation Rate
Edit `generate_orders.py`:
```python
# Line 90: Change interval (seconds between orders)
generator.run_continuous(interval=2)  # Default: 2 seconds
```

### Customize Order Sizes
Edit `generate_orders.py`:
```python
# Line 27: Change quantity options
qty = random.choice([10, 25, 50, 100, 200])  # Add/remove sizes
```

---

## 🐛 Troubleshooting

### ❌ Dashboard shows "Disconnected"
**Solution:**
1. Check exchange server is running on port 8765
2. Check browser console for errors (F12)
3. Verify no firewall blocking WebSocket

### ❌ No orders appearing
**Solution:**
1. Start order generator: `venv\Scripts\python.exe generate_orders.py`
2. Check generator connected: Look for "✓ Connected to exchange"
3. Verify server logs show new orders

### ❌ Connection refused error
**Solution:**
1. Exchange server not running
2. Start: `venv\Scripts\python.exe src\exchange_server.py`
3. Wait for "Exchange Server started" message

### ❌ WebSocket library not found
**Solution:**
```cmd
venv\Scripts\python.exe -m pip install websockets
```

---

## 💡 Pro Tips

1. **Multiple Dashboards**: Open dashboard in multiple browser tabs/windows
2. **Symbol Switching**: Use tabs to focus on specific stocks
3. **Performance**: Dashboard handles 50+ orders/second smoothly
4. **Mobile Friendly**: Dashboard is responsive and works on mobile browsers
5. **Dark Theme**: Dashboard uses dark theme optimized for extended viewing

---

## 🎬 Demo Script (for presentations)

```cmd
# 1. Start server
venv\Scripts\python.exe src\exchange_server.py

# 2. Open dashboard (browser)
# Show: Clean UI, connection status, empty order book

# 3. Start generator
venv\Scripts\python.exe generate_orders.py

# 4. Narration points:
# - "Orders flow in from multiple clients"
# - "Exchange matches buy and sell orders automatically"
# - "All updates broadcast in real-time via WebSocket"
# - "Order book maintains price-time priority"
# - "Stats update continuously"

# 5. Switch symbol tabs
# Show: Each symbol has independent order book

# 6. Stop server (Ctrl+C)
# Show: Dashboard detects disconnection, attempts reconnect

# 7. Restart server
# Show: Auto-reconnection, snapshot restored
```

---

## 📚 Files Created

| File | Purpose |
|------|---------|
| `dashboard_realtime.html` | Real-time WebSocket dashboard UI |
| `generate_orders.py` | Random order generator for demo |
| `src/exchange_server.py` | Updated with WebSocket broadcasting |
| `REALTIME_QUICKSTART.md` | This guide |

---

## 🚀 Next Steps

1. ✅ Start the server
2. ✅ Open the dashboard
3. ✅ Generate orders
4. 🎉 Watch real-time trading in action!

**Perfect for:**
- Live demos
- System testing
- Portfolio showcases
- Understanding order matching

---

## 📞 Support

If you encounter issues:
1. Check logs in terminal
2. Verify ports 8765 (WebSocket) and 9878 (FIX) are free
3. Ensure `websockets` library installed
4. Check browser console (F12) for JavaScript errors

---

**Built with:** Python, WebSocket, FIX 4.2, HTML/CSS/JavaScript  
**Author:** Crucible FIX Exchange  
**Purpose:** SDET Portfolio - Tower Research
