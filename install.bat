@echo off
echo ===================================================
echo USB Phone Webcam - Python Setup
echo ===================================================
echo.

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.11 or newer from https://www.python.org/downloads/
    echo Make sure to check "Add python.exe to PATH" during installation!
    pause
    exit /b 1
)

echo [OK] Python is installed.
echo.

if not exist venv\ (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

echo.
echo Installing requirements...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ===================================================
echo Installation complete! You can now run run.bat
echo ===================================================
pause
