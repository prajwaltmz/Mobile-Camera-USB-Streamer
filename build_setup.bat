@echo off
echo Building Mobile Camera MSI Setup...
call venv\Scripts\activate.bat
python setup.py bdist_msi
echo Build Complete. You can find the MSI installer in the 'dist' folder.
pause
