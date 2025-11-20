@echo off
REM FIX Exchange Test Suite Runner for Windows
REM Automates server startup, test execution, and cleanup

setlocal enabledelayedexpansion

echo ============================================
echo FIX Exchange Conformance Test Suite
echo ============================================
echo.

REM Get project root
cd /d "%~dp0\.."
set PROJECT_ROOT=%CD%

REM Configuration
set SERVER_SCRIPT=src\exchange_server.py
set SERVER_PORT=9878
set SERVER_LOG=server.log
set SERVER_PID_FILE=server.pid

echo Project root: %PROJECT_ROOT%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

echo Using Python: 
python --version
echo.

REM Activate virtual environment
if not exist "venv" (
    echo Warning: Virtual environment not found, creating...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo Virtual environment activated
echo.

REM Clean up any existing server processes
echo Checking for existing server processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%SERVER_PORT%" ^| findstr "LISTENING"') do (
    echo Found process on port %SERVER_PORT%: %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

REM Start the exchange server
echo ============================================
echo Starting Exchange Server...
echo ============================================

start /B "" python %SERVER_SCRIPT% > %SERVER_LOG% 2>&1

REM Wait for server to be ready
echo Waiting for server to be ready...
set ATTEMPT=0
set MAX_ATTEMPTS=30

:wait_loop
set /a ATTEMPT+=1
if %ATTEMPT% gtr %MAX_ATTEMPTS% (
    echo Error: Server failed to start within timeout
    echo Server log output:
    type %SERVER_LOG%
    goto cleanup_and_exit
)

REM Check if port is listening
netstat -ano | findstr ":%SERVER_PORT%" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo|set /p="."
    timeout /t 1 /nobreak >nul
    goto wait_loop
)

echo.
echo Server is ready!
echo.

REM Run the test suite
echo ============================================
echo Running Test Suite...
echo ============================================
echo.

behave features\ %*
set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================
echo Test Execution Complete
echo ============================================
echo.

REM Display server log if tests failed
if %TEST_EXIT_CODE% neq 0 (
    echo Server log output:
    type %SERVER_LOG%
    echo.
)

:cleanup_and_exit
REM Cleanup
echo ============================================
echo Cleaning up...
echo ============================================

REM Kill server processes
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%SERVER_PORT%" ^| findstr "LISTENING"') do (
    echo Stopping server process: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo Cleanup complete
echo.

exit /b %TEST_EXIT_CODE%
