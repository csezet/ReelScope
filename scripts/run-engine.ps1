# scripts/run-engine.ps1
# Runs the ReelScope Python Analytics Engine locally with dynamic or fixed port

param (
    [int]$Port = 8000,
    [string]$Token = ""
)

$ErrorActionPreference = "Stop"

$VenvPython = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "Virtual environment not found. Please run .\scripts\bootstrap.ps1 first."
}

$env:REELSCOPE_TOKEN = $Token
Write-Host "Starting ReelScope Engine on http://127.0.0.1:$Port (Token: $Token)..." -ForegroundColor Cyan

& $VenvPython -m reelscope_engine --host 127.0.0.1 --port $Port
