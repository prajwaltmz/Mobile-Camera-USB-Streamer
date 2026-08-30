@echo off
echo ===================================================
echo USB Phone Webcam - Server
echo ===================================================

if not exist venv\ (
    echo [ERROR] Virtual environment not found. Please run install.bat first!
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting server...
python server\server.py

pause
