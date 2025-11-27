@echo off
REM Crucible Exchange - Complete System Startup
REM Starts Exchange Server, WebSocket, and REST API Server

echo ================================================================================
echo CRUCIBLE FIX EXCHANGE - COMPLETE SYSTEM STARTUP
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate.bat
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Kill any existing Python processes on our ports
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":9878" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8765" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
timeout /t 1 /nobreak >nul

echo.
echo [1/2] Starting Exchange Server (FIX + WebSocket)...
echo       - FIX Protocol:   127.0.0.1:9878
echo       - WebSocket:      ws://127.0.0.1:8765
start "Crucible Exchange Server" cmd /k "venv\Scripts\python.exe src\exchange_server.py"
timeout /t 4 /nobreak >nul

echo.
echo [2/2] Starting REST API Server...
echo       - REST API:       http://127.0.0.1:5000
start "Crucible API Server" cmd /k "venv\Scripts\python.exe src\api_server.py"
timeout /t 2 /nobreak >nul

echo.
echo ================================================================================
echo   CRUCIBLE EXCHANGE SYSTEM - ALL SERVICES RUNNING
echo ================================================================================
echo.
echo Services:
echo   [OK] FIX Protocol Server    - 127.0.0.1:9878
echo   [OK] WebSocket Server       - ws://127.0.0.1:8765
echo   [OK] REST API Server        - http://127.0.0.1:5000
echo.
echo Dashboard:
echo   Open dashboard_minimal.html in your web browser
echo.
echo API Endpoints:
echo   http://127.0.0.1:5000/api/health
echo   http://127.0.0.1:5000/api/orderbook
echo   http://127.0.0.1:5000/api/orders
echo   http://127.0.0.1:5000/api/executions
echo   http://127.0.0.1:5000/api/submit_order
echo.
echo Testing:
echo   Run: behave features/
echo.
echo ================================================================================
echo.
echo Press any key to STOP all services...
pause >nul

echo.
echo Stopping all services...
taskkill /F /FI "WINDOWTITLE eq Crucible*" >nul 2>&1
echo All services stopped.
echo.
pause
