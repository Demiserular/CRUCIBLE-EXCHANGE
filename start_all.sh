#!/bin/bash
# Crucible Exchange - Complete System Startup
# Starts Exchange Server, WebSocket, and REST API Server

echo "================================================================================"
echo "CRUCIBLE FIX EXCHANGE - COMPLETE SYSTEM STARTUP"
echo "================================================================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/python" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python -m venv venv"
    echo "Then: source venv/bin/activate"
    echo "Then: pip install -r requirements.txt"
    exit 1
fi

# Kill any existing processes on our ports
echo "Cleaning up existing processes..."
lsof -ti:9878 | xargs kill -9 2>/dev/null || true
lsof -ti:8765 | xargs kill -9 2>/dev/null || true
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
sleep 1

echo ""
echo "[1/2] Starting Exchange Server (FIX + WebSocket)..."
echo "      - FIX Protocol:   127.0.0.1:9878"
echo "      - WebSocket:      ws://127.0.0.1:8765"
venv/bin/python src/exchange_server.py > logs/exchange.log 2>&1 &
EXCHANGE_PID=$!
echo "      Exchange Server started (PID: $EXCHANGE_PID)"
sleep 3

echo ""
echo "[2/2] Starting REST API Server..."
echo "      - REST API:       http://127.0.0.1:5000"
venv/bin/python src/api_server.py > logs/api.log 2>&1 &
API_PID=$!
echo "      API Server started (PID: $API_PID)"
sleep 2

echo ""
echo "================================================================================"
echo "  CRUCIBLE EXCHANGE SYSTEM - ALL SERVICES RUNNING"
echo "================================================================================"
echo ""
echo "Services:"
echo "  [OK] FIX Protocol Server    - 127.0.0.1:9878 (PID: $EXCHANGE_PID)"
echo "  [OK] WebSocket Server       - ws://127.0.0.1:8765"
echo "  [OK] REST API Server        - http://127.0.0.1:5000 (PID: $API_PID)"
echo ""
echo "Dashboard:"
echo "  Open dashboard_minimal.html in your web browser"
echo ""
echo "API Endpoints:"
echo "  http://127.0.0.1:5000/api/health"
echo "  http://127.0.0.1:5000/api/orderbook"
echo "  http://127.0.0.1:5000/api/orders"
echo "  http://127.0.0.1:5000/api/executions"
echo "  http://127.0.0.1:5000/api/submit_order"
echo ""
echo "Testing:"
echo "  Run: behave features/"
echo ""
echo "Logs:"
echo "  Exchange: logs/exchange.log"
echo "  API:      logs/api.log"
echo ""
echo "================================================================================"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Create a trap to catch Ctrl+C and stop services
trap "echo ''; echo 'Stopping all services...'; kill $EXCHANGE_PID $API_PID 2>/dev/null; echo 'All services stopped.'; exit 0" INT TERM

# Wait for user interrupt
wait
