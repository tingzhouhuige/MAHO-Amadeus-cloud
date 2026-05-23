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
}
