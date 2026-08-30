@echo off
echo ===================================================
echo USB Phone Webcam - VB-Audio Virtual Cable Uninstaller
echo ===================================================
echo.
echo NOTE: You must run this script as Administrator!
echo.
pause

echo.
echo Uninstalling VB-Audio Virtual Cable...
if exist VBCable_Setup\VBCABLE_Setup_x64.exe (
    echo Running VB-Audio uninstaller...
    cd VBCable_Setup
    start /wait VBCABLE_Setup_x64.exe -u -h
    cd ..
) else (
    echo [WARNING] Could not find downloaded VB-Audio setup files.
    echo Trying to uninstall via Windows Package Manager...
    winget uninstall "VB-Audio Virtual Cable"
)

echo.
echo ===================================================
echo VB-Audio Virtual Cable uninstallation complete!
echo If it failed to uninstall, please remove it manually
echo from Windows Settings -^> Apps -^> Installed Apps.
echo Please restart your computer if requested.
echo ===================================================
pause
