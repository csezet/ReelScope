# scripts/build-engine.ps1
# Builds the Python analytics engine as a standalone onedir bundle using PyInstaller

$ErrorActionPreference = "Stop"

Write-Host "Checking virtual environment..." -ForegroundColor Cyan
$PythonExe = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Write-Host "Ensuring PyInstaller is installed..." -ForegroundColor Cyan
& $PythonExe -m pip install --quiet pyinstaller

$EngineDir = Join-Path $PSScriptRoot "..\engine"
$SqlDir = Join-Path $PSScriptRoot "..\sql"
$DistDir = Join-Path $PSScriptRoot "..\dist"
$AssetsEngineDir = Join-Path $PSScriptRoot "..\src\ReelScope.App\Assets\Engine\reelscope-engine"

Write-Host "Running PyInstaller onedir build..." -ForegroundColor Cyan
& $PythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --name reelscope-engine `
    --distpath $DistDir `
    --add-data "$SqlDir;sql" `
    --hidden-import "duckdb" `
    --hidden-import "uvicorn" `
    --hidden-import "uvicorn.logging" `
    --hidden-import "uvicorn.loops.auto" `
    --hidden-import "uvicorn.protocols.http.auto" `
    --hidden-import "uvicorn.protocols.websockets.auto" `
    --hidden-import "uvicorn.lifespans.on" `
    --hidden-import "scipy.special.cython_special" `
    --hidden-import "sklearn.utils._typedefs" `
    --collect-submodules "reelscope_engine" `
    --collect-data "duckdb" `
    --paths $EngineDir `
    "$EngineDir\reelscope_engine\__main__.py"

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed with exit code $LASTEXITCODE"
}

Write-Host "Copying engine bundle to WinUI Assets directory..." -ForegroundColor Cyan
if (Test-Path $AssetsEngineDir) {
    Remove-Item -Path $AssetsEngineDir -Recurse -Force
}
New-Item -ItemType Directory -Path (Split-Path $AssetsEngineDir) -Force | Out-Null
Copy-Item -Path (Join-Path $DistDir "reelscope-engine") -Destination $AssetsEngineDir -Recurse -Force

Write-Host "Engine build and packaging complete: $AssetsEngineDir" -ForegroundColor Green
