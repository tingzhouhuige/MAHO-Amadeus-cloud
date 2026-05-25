$ErrorActionPreference = "SilentlyContinue"

$root = Split-Path -Parent $PSScriptRoot
$pidDir = Join-Path $root ".runtime"

foreach ($name in @("backend", "frontend")) {
    $pidFile = Join-Path $pidDir "$name.pid"
    if (Test-Path -LiteralPath $pidFile) {
        $pidValue = Get-Content -LiteralPath $pidFile -Raw
        if ($pidValue) {
            Stop-Process -Id ([int]$pidValue.Trim()) -Force
        }
        Remove-Item -LiteralPath $pidFile -Force
    }
}

foreach ($port in @(8080, 5173)) {
    Get-NetTCPConnection -LocalPort $port -State Listen |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object { Stop-Process -Id $_ -Force }

    netstat -ano |
        Select-String (":$port\s") |
        ForEach-Object {
            $parts = ($_ -split "\s+") | Where-Object { $_ }
            if ($parts.Length -ge 5 -and $parts[1] -match ":$port$" -and $parts[3] -eq "LISTENING") {
                Stop-Process -Id ([int]$parts[4]) -Force
            }
        }
}

$root = Split-Path -Parent $PSScriptRoot
$mapping = cmd.exe /c subst | Select-String -SimpleMatch "M:\"
if ($mapping -and $mapping.Line -match [regex]::Escape($root)) {
    cmd.exe /c "subst M: /D" | Out-Null
}
