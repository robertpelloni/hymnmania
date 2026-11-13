@echo off
setlocal
cd /d "%~dp0"
if not exist logs mkdir logs
set "PY_EXE=python"
if exist "C:\Python314\python.exe" set "PY_EXE=C:\Python314\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe" set "PY_EXE=C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe"
"%PY_EXE%" suno_throttle.py --run --n 1 >> logs\suno_throttle.log 2>&1
endlocal
