@echo off
:: Ensure that the script runs in the same directory as the batch file
cd /d %~dp0

echo "DEBUG: install.bat has been launched" > C:\install_bat.log

:: Execute the winrm setup script
powershell -ExecutionPolicy Bypass -File "setup_winrm.ps1"

@REM :: Execute the OSIR setup script
@REM powershell -ExecutionPolicy Bypass -File "setup_OSIR.ps1"


