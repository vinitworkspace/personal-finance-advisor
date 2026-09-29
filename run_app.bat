@echo off
title Personal Finance Advisor Bot
echo ======================================================================
echo             Personal Finance Advisor Bot - Browser Launcher
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Activate virtual environment if present
if exist venv\Scripts\activate.bat (
    echo [OK] Activating virtual environment (venv)...
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    echo [OK] Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
)

:: 2. Launch the Python browser launcher
echo [OK] Starting Flask Server and launching browser...
python run_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application terminated with error code %ERRORLEVEL%.
    pause
)
