#!/bin/bash

echo "Setting up QR Code Analytics Backend..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo
    echo "IMPORTANT: Please edit .env file with your SMTP settings before running the application!"
    echo
fi

# Run the application
echo "Starting Flask application..."
echo
python3 run.py