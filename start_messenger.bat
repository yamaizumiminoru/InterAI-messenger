@echo off
echo Starting Messenger Mode MVP...
cd /d "%~dp0backend"

:: Open Browser
start "" "http://127.0.0.1:8000"

:: Start Backend
python main.py

pause
