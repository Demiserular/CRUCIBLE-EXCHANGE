#!/bin/bash
# FIX Exchange Test Suite Runner
# Automates server startup, test execution, and cleanup

set -e

echo "============================================"
echo "FIX Exchange Conformance Test Suite"
echo "============================================"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER_SCRIPT="src/exchange_server.py"
SERVER_PORT=9878
SERVER_LOG="server.log"
SERVER_PID=""

# Cleanup function
cleanup() {
    echo ""
    echo "============================================"
    echo "Cleaning up..."
    echo "============================================"
    
    # Kill server if running
    if [ ! -z "$SERVER_PID" ]; then
        echo "Stopping exchange server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
        echo "✓ Server stopped"
    fi
    
    # Kill any orphaned processes on port
    echo "Checking for orphaned processes on port $SERVER_PORT..."
    ORPHAN_PIDS=$(lsof -ti:$SERVER_PORT 2>/dev/null || true)
    if [ ! -z "$ORPHAN_PIDS" ]; then
        echo "Killing orphaned processes: $ORPHAN_PIDS"
        kill -9 $ORPHAN_PIDS 2>/dev/null || true
    fi
    
    echo "✓ Cleanup complete"
}

# Register cleanup on exit
trap cleanup EXIT INT TERM

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

echo "Using Python: $(which python3)"
echo "Python version: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found, creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "✓ Virtual environment activated"
echo ""

# Clean up any existing server processes
echo "Checking for existing server processes..."
EXISTING_PIDS=$(lsof -ti:$SERVER_PORT 2>/dev/null || true)
if [ ! -z "$EXISTING_PIDS" ]; then
    echo "Found existing processes on port $SERVER_PORT: $EXISTING_PIDS"
    kill -9 $EXISTING_PIDS 2>/dev/null || true
    sleep 1
fi

# Start the exchange server
echo "============================================"
echo "Starting Exchange Server..."
echo "============================================"
python3 $SERVER_SCRIPT > $SERVER_LOG 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"
echo "Server log: $SERVER_LOG"
echo ""

# Wait for server to be ready
echo "Waiting for server to be ready..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if nc -z 127.0.0.1 $SERVER_PORT 2>/dev/null; then
        echo -e "${GREEN}✓ Server is ready!${NC}"
        break
    fi
    
    # Check if server process died
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo -e "${RED}✗ Server process died during startup${NC}"
        echo "Server log output:"
        cat $SERVER_LOG
        exit 1
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 0.5
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}✗ Server failed to start within timeout${NC}"
    echo "Server log output:"
    cat $SERVER_LOG
    exit 1
fi

echo ""

# Run the test suite
echo "============================================"
echo "Running Test Suite..."
echo "============================================"
echo ""

behave features/ "$@"
TEST_EXIT_CODE=$?

echo ""
echo "============================================"
echo "Test Execution Complete"
echo "============================================"
echo ""

# Display server log if tests failed
if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "Server log (last 50 lines):"
    tail -50 $SERVER_LOG
    echo ""
fi

exit $TEST_EXIT_CODE
