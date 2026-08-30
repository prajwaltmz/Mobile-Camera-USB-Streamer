@echo off
echo ===================================================
echo USB Phone Webcam - Unity Video Capture Uninstaller
echo ===================================================
echo.
echo Uninstalling driver...
cd UnityCapture\UnityCapture-master\Install
call Uninstall.bat

cd ..\..\..
rmdir /s /q UnityCapture
echo.
echo ===================================================
echo Unity Video Capture uninstallation complete!
echo ===================================================
pause
