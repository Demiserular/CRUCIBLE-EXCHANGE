@echo off
REM Stop all Crucible Exchange services

echo Stopping Crucible Exchange System...

taskkill /F /IM python.exe >nul 2>&1

echo All services stopped.
