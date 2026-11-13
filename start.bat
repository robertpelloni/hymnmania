@echo off
setlocal
REM HymnMania root launcher - pass arguments to scheduler_v2.py (defaults to --status).
cd /d "%~dp0"
set "PY_EXE=python"
if exist "C:\Python314\python.exe" set "PY_EXE=C:\Python314\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe" set "PY_EXE=C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe"
if "%~1"=="" (
    "%PY_EXE%" scheduler_v2.py --status
) else (
    "%PY_EXE%" scheduler_v2.py %*
)
endlocal
