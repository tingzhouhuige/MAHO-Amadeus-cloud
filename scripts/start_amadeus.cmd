@echo off
setlocal

set "ROOT=%~dp0.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\scripts\start_maho.ps1"
if errorlevel 1 (
  echo Failed to start MAHO.
  pause
  exit /b 1
)

echo MAHO is starting in background.
echo Frontend URL: http://127.0.0.1:5173
pause
