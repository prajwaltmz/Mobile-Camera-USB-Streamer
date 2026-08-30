@echo off
echo ===================================================
echo USB Phone Webcam - Unity Video Capture Installer
echo ===================================================
echo.
echo Downloading Unity Video Capture...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/schellingb/UnityCapture/archive/refs/heads/master.zip' -OutFile 'UnityCapture.zip'"

echo Extracting files...
powershell -Command "Expand-Archive -Path 'UnityCapture.zip' -DestinationPath 'UnityCapture' -Force"

echo Installing driver...
cd UnityCapture\UnityCapture-master\Install
call Install.bat

cd ..\..\..
del UnityCapture.zip
echo.
echo ===================================================
echo Unity Video Capture installation complete!
echo ===================================================
pause
