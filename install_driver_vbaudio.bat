@echo off
echo ===================================================
echo USB Phone Webcam - VB-Audio Virtual Cable Installer
echo ===================================================
echo.
echo This script will install the VB-Audio Virtual Cable, 
echo which is required for the virtual microphone.
echo.
echo NOTE: You must run this script as Administrator!
echo.
pause

echo.
echo Downloading VB-Audio Virtual Cable...
if not exist VBCable_Setup.zip (
    curl -L "https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack43.zip" -o VBCable_Setup.zip
)

echo Extracting VB-Audio Virtual Cable...
powershell -command "Expand-Archive -Force -Path 'VBCable_Setup.zip' -DestinationPath 'VBCable_Setup'"

echo Installing VB-Audio Virtual Cable...
echo Please accept the Windows Security prompt to install the driver.
cd VBCable_Setup
if exist VBCABLE_Setup_x64.exe (
    start /wait VBCABLE_Setup_x64.exe -i -h
) else (
    echo [ERROR] Could not find VB-Audio setup executable. Please install manually from https://vb-audio.com/Cable/
)
cd ..

echo.
echo ===================================================
echo VB-Audio Virtual Cable installation complete!
echo Please restart your computer if requested.
echo ===================================================
pause
