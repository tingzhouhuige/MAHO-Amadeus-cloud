param(
    [ValidateSet("maho", "mayuri")]
    [string]$Role = ""
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$frontendWorkdir = $frontend
$frontendDrive = "M:"
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

    netstat -ano |
        Select-String (":$port\s") |
        ForEach-Object {
            $parts = ($_ -split "\s+") | Where-Object { $_ }
            if ($parts.Length -ge 5 -and $parts[1] -match ":$port$" -and $parts[3] -eq "LISTENING") {
                try { Stop-Process -Id ([int]$parts[4]) -Force -ErrorAction Stop } catch {}
            }
        }
}

function Quote-Cmd([string]$value) {
    '"' + ($value -replace '"', '\"') + '"'
}

function Select-Role {
    if ($Role) {
        $role = $Role.Trim().ToLower()
    } else {
        Write-Host ""
        Write-Host "Select role:"
        Write-Host "  1. Maho"
        Write-Host "  2. Mayuri"
        $choice = (Read-Host "Enter 1 or 2; press Enter for Maho").Trim()
        switch ($choice) {
            "2" { $role = "mayuri" }
            default { $role = "maho" }
        }
    }

    switch ($role) {
        "mayuri" { return @{ Key = "mayuri"; Name = "Mayuri" } }
        default { return @{ Key = "maho"; Name = "Maho" } }
    }
}

function Use-FrontendPathWithoutSpaces {
    if ($root -notmatch "\s") {
        return
    }

    $existing = cmd.exe /c subst | Select-String -SimpleMatch "$frontendDrive\:"
    if ($existing -and $existing.Line -notmatch [regex]::Escape($root)) {
        throw "$frontendDrive is already mapped to another path. Please free it before starting MAHO."
    }

    if (-not $existing) {
        cmd.exe /c "subst $frontendDrive ""$root""" | Out-Null
    }

    $script:frontendWorkdir = "$frontendDrive\frontend"
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

$roleInfo = Select-Role
$roleKey = $roleInfo.Key
Use-FrontendPathWithoutSpaces

Set-Content -LiteralPath $backendOut -Value "" -Encoding UTF8
Set-Content -LiteralPath $backendErr -Value "" -Encoding UTF8
Set-Content -LiteralPath $frontendOut -Value "" -Encoding UTF8
Set-Content -LiteralPath $frontendErr -Value "" -Encoding UTF8

$shell = New-Object -ComObject WScript.Shell
$roleEnv = "set MAHO_ROLE=$roleKey&& set VITE_MAHO_ROLE=$roleKey&& "
$backendCmd = "cmd.exe /c $roleEnv cd /d $(Quote-Cmd $backend) && $(Quote-Cmd $python) main.py > $(Quote-Cmd $backendOut) 2> $(Quote-Cmd $backendErr)"
$frontendCmd = "cmd.exe /c $roleEnv cd /d $(Quote-Cmd $frontendWorkdir) && $(Quote-Cmd $npm) run dev -- --host 127.0.0.1 --configLoader native > $(Quote-Cmd $frontendOut) 2> $(Quote-Cmd $frontendErr)"

[void]$shell.Run($backendCmd, 0, $false)
[void]$shell.Run($frontendCmd, 0, $false)

Write-Host "Selected role: $($roleInfo.Name) ($roleKey)"
Write-Host "Backend:  http://127.0.0.1:8080"
Write-Host "Frontend: http://127.0.0.1:5173"
