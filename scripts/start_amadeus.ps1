$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Models = Join-Path $Backend "models"
$Tmp = Join-Path $Models ".tmp"
$OllamaStore = Join-Path $Models "ollama-store"
$OllamaExe = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
$OllamaDir = Split-Path $OllamaExe -Parent
$CudaDir = Join-Path $OllamaDir "lib\ollama\cuda_v13"
$Python = Join-Path $Backend ".venv\Scripts\python.exe"
$NpmCmd = "C:\Program Files\nodejs\npm.cmd"

New-Item -ItemType Directory -Force -Path $Tmp | Out-Null

function Start-AmadeusProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FileName,
        [Parameter(Mandatory = $true)][string]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory
    )

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $FileName
    $psi.Arguments = $Arguments
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    $null = $process.Start()
    return $process.Id
}

function Test-PortListening {
    param([Parameter(Mandatory = $true)][int]$Port)

    $pattern = ":$Port "
    $lines = netstat -ano | Select-String -SimpleMatch $pattern
    return [bool]($lines | Where-Object { $_.Line -match "\sLISTENING\s" })
}

$env:TEMP = $Tmp
$env:TMP = $Tmp
$env:OLLAMA_TMPDIR = $Tmp
$env:OLLAMA_HOST = "127.0.0.1:11434"
$env:OLLAMA_MODELS = $OllamaStore
$env:OLLAMA_LLM_LIBRARY = "cuda_v13"
$env:CUDA_VISIBLE_DEVICES = "0"
$env:PATH = "$CudaDir;$OllamaDir;$env:PATH"

if (-not (Test-PortListening 11434)) {
    $ollamaPid = Start-AmadeusProcess `
        -FileName $OllamaExe `
        -Arguments "serve" `
        -WorkingDirectory $Root
    Start-Sleep -Seconds 3
} else {
    $ollamaPid = "already-running"
}

if (-not (Test-PortListening 8080)) {
    $backendPid = Start-AmadeusProcess `
        -FileName $Python `
        -Arguments "-m uvicorn main:app --host 0.0.0.0 --port 8080" `
        -WorkingDirectory $Backend
} else {
    $backendPid = "already-running"
}

if (-not (Test-PortListening 5173)) {
    $frontendPid = Start-AmadeusProcess `
        -FileName $NpmCmd `
        -Arguments "run dev -- --host 127.0.0.1" `
        -WorkingDirectory $Frontend
} else {
    $frontendPid = "already-running"
}

Write-Host "MAHO-Amadeus starting..."
Write-Host "Ollama:   $ollamaPid"
Write-Host "Backend:  $backendPid"
Write-Host "Frontend: $frontendPid"
Write-Host "Frontend URL: http://127.0.0.1:5173"
