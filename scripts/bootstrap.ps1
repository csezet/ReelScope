# scripts/bootstrap.ps1
# Sets up Python virtual environment and installs dependencies

$ErrorActionPreference = "Stop"

Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
python -m venv .venv

$VenvPython = ".\.venv\Scripts\python.exe"
Write-Host "Upgrading pip..." -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip

Write-Host "Installing dependencies from engine\requirements-lock.txt..." -ForegroundColor Cyan
& $VenvPython -m pip install -r engine\requirements-lock.txt

Write-Host "ReelScope Engine bootstrap complete!" -ForegroundColor Green
