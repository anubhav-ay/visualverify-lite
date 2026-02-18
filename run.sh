#!/bin/bash

echo ""
echo "========================================"
echo "  VisualVerify Lite - Starting..."
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python not found! Install Python 3.9+"
    exit 1
fi

# Check dependencies
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Starting server..."
echo "Open browser: http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

python3 main.py
