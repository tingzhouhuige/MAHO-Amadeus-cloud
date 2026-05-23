$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$python = Join-Path $backend ".venv\Scripts\python.exe"
$npm = "C:\Program Files\nodejs\npm.cmd"
$backendOut = Join-Path $backend "maho-backend.out.log"
$backendErr = Join-Path $backend "maho-backend.err.log"
$frontendOut = Join-Path $frontend "maho-frontend.out.log"
$frontendErr = Join-Path $frontend "maho-frontend.err.log"

function Stop-PortProcess([int]$port) {
    Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object {
            try { Stop-Process -Id $_ -Force -ErrorAction Stop } catch {}
        }
}

function Quote-Cmd([string]$value) {
    '"' + ($value -replace '"', '\"') + '"'
}

if (-not (Test-Path -LiteralPath $python)) {
    throw "Backend Python not found: $python"
}
if (-not (Test-Path -LiteralPath $npm)) {
    throw "npm not found: $npm"
}

Stop-PortProcess 8080
Stop-PortProcess 5173

Get-Process -Name "ollama","ollama app" -ErrorAction SilentlyContinue |
    Stop-Process -Force -ErrorAction SilentlyContinue

Set-Content -LiteralPath $backendOut -Value "" -Encoding UTF8
Set-Content -LiteralPath $backendErr -Value "" -Encoding UTF8
Set-Content -LiteralPath $frontendOut -Value "" -Encoding UTF8
Set-Content -LiteralPath $frontendErr -Value "" -Encoding UTF8

$shell = New-Object -ComObject WScript.Shell
$backendCmd = "cmd.exe /c cd /d $(Quote-Cmd $backend) && $(Quote-Cmd $python) main.py > $(Quote-Cmd $backendOut) 2> $(Quote-Cmd $backendErr)"
$frontendCmd = "cmd.exe /c cd /d $(Quote-Cmd $frontend) && $(Quote-Cmd $npm) run dev -- --host 127.0.0.1 > $(Quote-Cmd $frontendOut) 2> $(Quote-Cmd $frontendErr)"

[void]$shell.Run($backendCmd, 0, $false)
[void]$shell.Run($frontendCmd, 0, $false)
