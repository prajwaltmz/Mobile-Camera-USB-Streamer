@echo off
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run install.bat first!
    pause
    exit /b
)
echo Starting Mobile Camera Server...
call venv\Scripts\activate
start "" pythonw server.py
exit /b
