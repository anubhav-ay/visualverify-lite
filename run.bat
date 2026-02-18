@echo off
echo.
echo ========================================
echo   VisualVerify Lite - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting server...
echo Open browser: http://localhost:8000
echo Press Ctrl+C to stop
echo.

python main.py

pause
