@echo off
setlocal
REM Reminds about the next pipeline move and logs NEXT_MOVE.md.
cd /d "%~dp0"
if not exist logs mkdir logs
echo ==== REMINDER %DATE% %TIME% ==== >> logs\reminder.log
type NEXT_MOVE.md >> logs\reminder.log 2>nul
powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('HymnMania REMINDER - Check pipeline queue and NEXT_MOVE.md.','HymnMania - next move',0,64)"
endlocal
