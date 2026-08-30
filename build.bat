@echo off
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run install.bat first!
    pause
    exit /b
)
echo Building Mobile Camera Executable...
call venv\Scripts\activate
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --add-data "server\cert.pem;." --add-data "server\key.pem;." --add-data "web\index.html;." --add-data "web\audio-processor.js;." --name "MobileCamera" --icon="icon.ico" server\server.py
echo Build Complete! You will find a single standalone app at: 'dist\MobileCamera.exe'
pause
