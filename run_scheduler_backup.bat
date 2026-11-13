@echo off
setlocal
REM HymnMania BACKUP posting runner (failover for HymnMania Daily Post).
REM Only posts if NOTHING was published today (checks .scheduler_log.json).
cd /d "%~dp0"
if not exist logs mkdir logs
set "PY_EXE=python"
if exist "C:\Python314\python.exe" set "PY_EXE=C:\Python314\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe" set "PY_EXE=C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe"
echo. >> logs\scheduler_backup.log
echo ==================== BACKUP %DATE% %TIME% ==================== >> logs\scheduler_backup.log
"%PY_EXE%" browser_watchdog.py >> logs\scheduler_backup.log 2>&1
"%PY_EXE%" -u scheduler_v2.py --catchup >> logs\scheduler_backup.log 2>&1
echo ---- exit %ERRORLEVEL% ---- >> logs\scheduler_backup.log
endlocal
