@echo off
echo 🚀 Starting ZOPKIT ReAct System...
echo ====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Start the ReAct system
echo 🔧 Initializing ReAct components...
python start_react_system.py

pause