@echo off
echo ===================================================
echo USB Phone Webcam - OBS Studio Installer
echo ===================================================
echo.
echo This script will install OBS Studio, which provides
echo the OBS Virtual Camera driver.
echo.
pause

echo Installing OBS Studio...
winget install OBSProject.OBSStudio

echo.
echo ===================================================
echo OBS Studio installation complete!
echo ===================================================
pause
