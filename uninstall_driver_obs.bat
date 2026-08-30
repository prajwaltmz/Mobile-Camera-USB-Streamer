@echo off
echo ===================================================
echo USB Phone Webcam - OBS Studio Uninstaller
echo ===================================================
echo.
echo This script will uninstall OBS Studio.
echo.
pause

echo Uninstalling OBS Studio...
winget uninstall OBSProject.OBSStudio

echo.
echo ===================================================
echo OBS Studio uninstallation complete!
echo ===================================================
pause
