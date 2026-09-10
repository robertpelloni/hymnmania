@echo off
REM HymnMania daily posting cycle — one ready track across all platforms.
REM Registered as Windows Scheduled Task "HymnMania Daily Post" (weekdays 3 PM).
cd /d C:\Users\jakeg\robertpelloni\hymnmania
if not exist logs mkdir logs
echo. >> logs\scheduler.log
echo ==================== %DATE% %TIME% ==================== >> logs\scheduler.log
"C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe" -u scheduler_v2.py --now 1 >> logs\scheduler.log 2>&1
echo ---- exit %ERRORLEVEL% ---- >> logs\scheduler.log
