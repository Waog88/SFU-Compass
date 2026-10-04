@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto check_modules

echo Preparing a local Python environment for SFU Navigator...
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 goto use_py
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if not errorlevel 1 goto use_python
echo Python 3.10 or newer is required for setup.
echo Install Python from https://www.python.org/downloads/windows/
echo Include pip and Tcl/Tk, then run this launcher again.
exit /b 1

:use_py
py -3 -m venv ".venv"
if errorlevel 1 exit /b 1
goto check_modules

:use_python
python -m venv ".venv"
if errorlevel 1 exit /b 1

:check_modules
".venv\Scripts\python.exe" -c "import tkinter" >nul 2>&1
if errorlevel 1 (
  echo Tkinter is missing. Modify your Python installation to include Tcl/Tk.
  exit /b 1
)
".venv\Scripts\python.exe" -c "import serial" >nul 2>&1
if not errorlevel 1 exit /b 0
echo Installing the serial dependency. Internet is needed on first setup.
".venv\Scripts\python.exe" -m pip install -r "python\requirements.txt"
if errorlevel 1 exit /b 1
exit /b 0
