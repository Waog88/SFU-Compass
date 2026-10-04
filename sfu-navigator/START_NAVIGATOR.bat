@echo off
setlocal
cd /d "%~dp0"
call "%~dp0SETUP_RUNTIME.bat"
if errorlevel 1 goto failed
"%~dp0.venv\Scripts\python.exe" "%~dp0python\launcher.py"
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo SFU Navigator could not start. Check the message above.
pause
exit /b 1
