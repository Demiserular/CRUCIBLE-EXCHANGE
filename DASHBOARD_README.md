# 🎨 FIX Exchange Trading Dashboard

A modern, real-time web dashboard for monitoring the FIX Exchange server activity.

## Features

### 📊 Live Statistics
- **Order Metrics**: Total orders, filled orders, open orders, trading volume
- **Performance Monitoring**: Latency, orders per second, active sessions, uptime
- **Portfolio Summary**: Total value, P&L, returns, positions

### 📈 Market Watch
- Real-time price updates for major stocks (AAPL, GOOGL, MSFT, AMZN, TSLA)
- Bid/Ask spreads
- Volume tracking
- Price changes with color-coded indicators

### 📝 Order Management
- Recent order list with real-time updates
- Order status tracking (New, Filled, Canceled)
- Side indication (Buy/Sell with color coding)
- Order details (symbol, quantity, price, fill status)

### 🎮 Interactive Controls
- **Generate Buy Order**: Create random buy orders
- **Generate Sell Order**: Create random sell orders
- **Generate Matching Pair**: Create orders that will match
- **Generate Trading Session**: Simulate active trading with multiple orders
- **Clear Orders**: Reset the order list

### 🖥️ Console Logs
- Real-time activity log
- Timestamped entries
- Server events and order execution tracking

## How to Use

### 1. Open the Dashboard

**Option A: Direct File Open**
```
Simply double-click dashboard.html
```

**Option B: With Python Server**
```bash
# From project root
cd c:\Users\sc895\Project\Crucible
python -m http.server 8000
```
Then open: http://localhost:8000/dashboard.html

**Option C: With VS Code Live Server**
- Right-click on `dashboard.html`
- Select "Open with Live Server"

### 2. Interact with the Dashboard

#### Generate Orders
Click any of the control buttons to:
- Create individual buy/sell orders
- Generate matching order pairs
- Simulate a full trading session

#### Monitor Activity
- Watch real-time statistics update
- View order execution in the console
- Track market data changes

#### Observe Order Flow
- Orders appear instantly in the "Recent Orders" panel
- Status changes from NEW → FILLED automatically
- Color coding: Green (Buy), Red (Sell)

## Sample Data Generator

The dashboard works with the `sample_data_generator.py` script for realistic data:

```bash
# Generate sample data
python sample_data_generator.py
```

### Sample Data Features

**Market Data Generation:**
- 10 major stocks with realistic prices
- Price movements based on random walk
- Bid/Ask spreads
- Volume data

**Order Generation:**
- Random order creation (Market/Limit)
- Realistic quantities and prices
- Buy/Sell order generation
- Matching order pairs

**Portfolio Generation:**
- Multi-position portfolios
- Cost basis and P&L calculation
- Current market values
- Return percentages

## Integration with Exchange Server

For **live** integration with the actual exchange server:

### 1. Start the Exchange Server
```bash
python src/exchange_server.py
```

### 2. Connect Client (Future Enhancement)
```javascript
// WebSocket connection (to be implemented)
const ws = new WebSocket('ws://localhost:9878');

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    updateDashboard(message);
};
```

## Technology Stack

- **Frontend**: Pure HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with gradient backgrounds
- **Animation**: CSS animations and transitions
- **Data Visualization**: Dynamic tables and cards
- **Responsive Design**: Mobile-friendly grid layout

## UI Components

### Cards
- **Statistics Cards**: Show key metrics
- **Market Watch Table**: Stock prices and changes
- **Order List**: Recent order activity
- **Control Panel**: Interactive buttons
- **Log Console**: Terminal-style activity log

### Color Scheme
- **Primary**: Purple gradient (#667eea → #764ba2)
- **Success**: Green (#10b981) - Positive changes, Buy orders
- **Danger**: Red (#ef4444) - Negative changes, Sell orders
- **Neutral**: Gray (#6b7280) - Inactive states

### Responsive Breakpoints
- Desktop: 1400px max width
- Tablet: Grid collapses to 2 columns
- Mobile: Single column layout

## Future Enhancements

### Planned Features
- [ ] WebSocket integration with exchange server
- [ ] Real-time order book visualization
- [ ] Interactive charting (price history)
- [ ] Order placement form
- [ ] Advanced filtering and search
- [ ] Export data to CSV
- [ ] Dark/Light theme toggle
- [ ] User authentication
- [ ] Multi-session support
- [ ] Alert notifications

### Advanced Visualizations
- [ ] Candlestick charts
- [ ] Depth chart (order book)
- [ ] Volume profile
- [ ] Time & Sales
- [ ] Heat map

## Screenshots

### Dashboard Overview
- Real-time statistics
- Market watch with live prices
- Recent order activity

### Control Panel
- One-click order generation
- Simulated trading sessions
- Activity logging

## Best Practices

1. **Performance**: Dashboard handles 100+ orders smoothly
2. **User Experience**: Instant feedback on all actions
3. **Data Presentation**: Clear, color-coded information
4. **Accessibility**: High contrast, readable fonts
5. **Responsiveness**: Works on all screen sizes

## Keyboard Shortcuts (Planned)
- `Ctrl+B`: Generate Buy Order
- `Ctrl+S`: Generate Sell Order
- `Ctrl+M`: Generate Matching Pair
- `Ctrl+T`: Generate Trading Session
- `Ctrl+C`: Clear Orders

## Testing the Dashboard

```bash
# Run automated tests (future)
pytest tests/test_dashboard.py

# Manual testing checklist:
# ✓ All buttons functional
# ✓ Orders appear in list
# ✓ Status updates work
# ✓ Logs scroll correctly
# ✓ Statistics update
# ✓ Responsive on mobile
```

## Contributing

To add new features to the dashboard:

1. Modify `dashboard.html`
2. Test in multiple browsers
3. Ensure mobile responsiveness
4. Update this README
5. Add integration tests

## License

Part of the Crucible FIX Exchange project.

---

**Built with ❤️ for SDET excellence and financial technology demonstration.**
