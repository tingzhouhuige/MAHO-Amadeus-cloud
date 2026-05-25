param(
    [ValidateSet("maho", "mayuri")]
    [string]$Role = ""
)

$ErrorActionPreference = "Stop"
$launcher = Join-Path $PSScriptRoot "start_maho.ps1"

if ($Role) {
    & $launcher -Role $Role
} else {
    & $launcher
}
