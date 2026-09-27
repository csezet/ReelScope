# scripts/build-app.ps1
# Compiles and publishes ReelScope.App for win-x64

param (
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"

$ProjectFile = Join-Path $PSScriptRoot "..\src\ReelScope.App\ReelScope.App.csproj"
$PublishDir = Join-Path $PSScriptRoot "..\dist\ReelScope-win-x64"

Write-Host "Publishing ReelScope.App ($Configuration, win-x64)..." -ForegroundColor Cyan

dotnet publish $ProjectFile `
    -c $Configuration `
    -r win-x64 `
    --self-contained true `
    -o $PublishDir

Write-Host "ReelScope.App published successfully to: $PublishDir" -ForegroundColor Green
