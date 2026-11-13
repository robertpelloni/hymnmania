@echo off
setlocal
REM HymnMania root build and verification script (preserves all built binaries).
cd /d "%~dp0"
set "PY_EXE=python"
if exist "C:\Python314\python.exe" set "PY_EXE=C:\Python314\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe" set "PY_EXE=C:\Users\jakeg\AppData\Local\Programs\Python\Python314\python.exe"
echo [1/3] Compiling Python pipeline scripts...
"%PY_EXE%" -m py_compile scheduler_v2.py post_to_youtube.py cap_cycle.py quick_composer.py suno_auth.py upload_robust2.py gen_only.py suno_throttle.py browser_watchdog.py cleanup_tabs.py social_media_mirror.py scripts\zernio_upload.py scripts\zernio_batch_upload.py scripts\zernio_tiktok_batch.py
if errorlevel 1 exit /b %ERRORLEVEL%
echo [2/3] Building TypeScript in submodules\ableton_psytrance_hymn_creator...
call npm --prefix submodules\ableton_psytrance_hymn_creator run build
if errorlevel 1 exit /b %ERRORLEVEL%
echo [3/3] Build complete (v5.97.41).
endlocal
