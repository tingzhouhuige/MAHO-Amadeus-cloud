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

echo.
echo 请选择启动角色：
echo   1. 比屋定真帆 MAHO
echo   2. 椎名真由理 Mayuri
choice /C 12 /N /M "输入 1 或 2: "
if errorlevel 2 (
  set "MAHO_ROLE=mayuri"
  echo 已选择：椎名真由理
) else (
  set "MAHO_ROLE=maho"
  echo 已选择：比屋定真帆
)

netstat -ano | findstr ":11434" >nul
if %errorlevel%==0 (
  taskkill /F /IM ollama.exe >nul 2>nul
  taskkill /F /IM "ollama app.exe" >nul 2>nul
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\start_maho.ps1" -Role "%MAHO_ROLE%"
if errorlevel 1 (
  echo MAHO 启动失败。
  pause
  exit /b 1
)

echo MAHO 正在后台启动。
echo 前端地址: http://127.0.0.1:5173
echo 如果页面暂时打不开，请等 5-10 秒后刷新。
pause
