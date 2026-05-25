@echo off
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "PY=%BACKEND%\.venv\Scripts\pythonw.exe"
set "NPM=C:\Program Files\nodejs\npm.cmd"

if not exist "%PY%" (
  echo Backend Python not found: "%PY%"
  pause
  exit /b 1
)

if not exist "%NPM%" (
  echo Node.js npm not found: "%NPM%"
  pause
  exit /b 1
)

echo.
echo Select role:
echo   1. Maho
echo   2. Mayuri
choice /C 12 /N /M "Enter 1 or 2: "
if errorlevel 2 (
  set "MAHO_ROLE=mayuri"
  echo Selected: Mayuri
) else (
  set "MAHO_ROLE=maho"
  echo Selected: Maho
)

netstat -ano | findstr ":11434" >nul
if %errorlevel%==0 (
  taskkill /F /IM ollama.exe >nul 2>nul
  taskkill /F /IM "ollama app.exe" >nul 2>nul
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\start_maho.ps1" -Role "%MAHO_ROLE%"
if errorlevel 1 (
  echo Failed to start MAHO.
  pause
  exit /b 1
)

echo MAHO is starting in background.
echo Frontend URL: http://127.0.0.1:5173
echo If the page is not ready, wait 5-10 seconds and refresh.
pause
