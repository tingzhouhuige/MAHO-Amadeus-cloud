@echo off
set "ROOT=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\stop_maho.ps1"
echo MAHO backend and frontend stopped.
pause
