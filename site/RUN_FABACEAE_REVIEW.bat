@echo off
setlocal
cd /d "%~dp0"
echo Fabaceae private reviewed-photo learner
echo -------------------------------------
echo Opening the no-cache local browser preview...
where py >nul 2>nul
if %errorlevel%==0 (
 start "" "http://127.0.0.1:8768/?species=senegalia-greggii"
 py -3 -m http.server 8768 --bind 127.0.0.1
) else (
 where python >nul 2>nul
 if errorlevel 1 (
  echo Python 3 is required. Install it or use the original Hays Botany launcher.
  pause
  exit /b 1
 )
 start "" "http://127.0.0.1:8768/?species=senegalia-greggii"
 python -m http.server 8768 --bind 127.0.0.1
)
