@echo off
setlocal
cd /d "%~dp0"
call "%~dp0SETUP_RUNTIME.bat"
if errorlevel 1 goto failed
echo Installing the Windows executable builder...
"%~dp0.venv\Scripts\python.exe" -m pip install "pyinstaller>=6,<7"
if errorlevel 1 goto failed
cd /d "%~dp0python"
"%~dp0.venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name SFU-Navigator --distpath "%~dp0dist" --workpath "%~dp0build" --specpath "%~dp0build" --paths "%~dp0python" --collect-submodules serial launcher.py
if errorlevel 1 goto failed
echo.
echo Built: %~dp0dist\SFU-Navigator.exe
echo This executable bundles Python and the routing code.
echo Keep the Arduino firmware uploaded and USB connected.
start "" "%~dp0dist"
pause
exit /b 0
:failed
echo.
echo The Windows executable build failed. Check the message above.
pause
exit /b 1
