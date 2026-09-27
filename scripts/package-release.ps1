# scripts/package-release.ps1
# Creates a distributable zip archive and SHA-256 checksum

param (
    [string]$Version = "0.1.0"
)

$ErrorActionPreference = "Stop"

$RootDir = Join-Path $PSScriptRoot ".."
$PublishDir = Join-Path $RootDir "dist\ReelScope-win-x64"
$ZipFile = Join-Path $RootDir "dist\ReelScope-v$Version-win-x64.zip"
$ShaFile = "$ZipFile.sha256"

if (-not (Test-Path $PublishDir)) {
    Write-Error "Published directory not found. Please run scripts\build-app.ps1 first."
}

# Copy license and notices into publish directory
Copy-Item (Join-Path $RootDir "LICENSE") $PublishDir -Force
Copy-Item (Join-Path $RootDir "THIRD_PARTY_NOTICES.txt") $PublishDir -Force

Write-Host "Creating release archive: $ZipFile..." -ForegroundColor Cyan
if (Test-Path $ZipFile) { Remove-Item $ZipFile -Force }
Compress-Archive -Path "$PublishDir\*" -DestinationPath $ZipFile

Write-Host "Computing SHA-256 checksum..." -ForegroundColor Cyan
$Hash = (Get-FileHash -Path $ZipFile -Algorithm SHA256).Hash
"$Hash  $([System.IO.Path]::GetFileName($ZipFile))" | Out-File -FilePath $ShaFile -Encoding utf8

Write-Host "Release packaged successfully!" -ForegroundColor Green
Write-Host "Archive:  $ZipFile" -ForegroundColor Green
Write-Host "Checksum: $Hash" -ForegroundColor Green
