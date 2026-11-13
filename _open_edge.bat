@echo off
setlocal
set "EDGE_EXE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE_EXE%" set "EDGE_EXE=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
start "" "%EDGE_EXE%" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\edge-cdp-profile" --no-first-run --no-default-browser-check
echo Edge CDP browser launched on port 9222 (%USERPROFILE%\edge-cdp-profile)
endlocal
