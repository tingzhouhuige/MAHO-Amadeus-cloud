@echo off
chcp 65001 >nul
set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "PY=%BACKEND%\.venv\Scripts\pythonw.exe"
set "NPM=C:\Program Files\nodejs\npm.cmd"

if not exist "%PY%" (
  echo 找不到后端 Python: "%PY%"
  pause
  exit /b 1
)

if not exist "%NPM%" (
  echo 找不到 Node.js npm: "%NPM%"
  pause
  exit /b 1
)

netstat -ano | findstr ":11434" >nul
if %errorlevel%==0 (
  taskkill /F /IM ollama.exe >nul 2>nul
  taskkill /F /IM "ollama app.exe" >nul 2>nul
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\start_maho.ps1"
echo MAHO 正在后台启动。
echo 前端地址: http://127.0.0.1:5173
echo 如果页面暂时打不开，请等 5-10 秒后刷新。
pause
