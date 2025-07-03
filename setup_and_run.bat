@echo off
echo Setting up QR Code Analytics Backend...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your SMTP settings before running the application!
    echo.
)

REM Run the application
echo Starting Flask application...
echo.
python run.py

pause