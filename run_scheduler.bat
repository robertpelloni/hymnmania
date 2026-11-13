@echo off
setlocal
REM HymnMania daily posting cycle - 6 tracks (6 fulls + 6 shorts) + all social platforms.
REM Registered as Windows Scheduled Task "HymnMania Daily Post" (weekdays 3 PM).
cd /d "%~dp0"
if not exist logs mkdir logs
set "PY_EXE=python"
if exist "C:\Python314\python.exe" set "PY_EXE=C:\Python314\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe" set "PY_EXE=C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe"
echo. >> logs\scheduler.log
echo ==================== %DATE% %TIME% ==================== >> logs\scheduler.log
"%PY_EXE%" -u scheduler_v2.py --now 6 >> logs\scheduler.log 2>&1
echo ---- exit %ERRORLEVEL% ---- >> logs\scheduler.log
endlocal
