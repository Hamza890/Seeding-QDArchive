# PowerShell script to help upload folders to GitHub
# This creates a clean copy without .venv and downloads folders

$sourcePath = Get-Location
$tempPath = Join-Path $env:TEMP "seeding-qdarchive-upload"

# Remove temp folder if it exists
if (Test-Path $tempPath) {
    Remove-Item $tempPath -Recurse -Force
}

# Create temp folder
New-Item -ItemType Directory -Path $tempPath | Out-Null

# Copy only the necessary folders and files
Write-Host "Copying files..." -ForegroundColor Green

# Copy folders
$folders = @("src", "config", "docs", "examples", "utils", "Datasets")
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Copy-Item $folder -Destination $tempPath -Recurse
        Write-Host "  Copied: $folder" -ForegroundColor Cyan
    }
}

# Copy root files
$files = @(
    ".gitignore",
    "README.md",
    "main.py",
    "requirements.txt",
    "overall_architecture_flow.png",
    "overall_architecture_simple.png",
    "overall_architecture_detailed.png"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $tempPath
        Write-Host "  Copied: $file" -ForegroundColor Cyan
    }
}

Write-Host "`nFiles copied to: $tempPath" -ForegroundColor Green
Write-Host "`nNow you can:" -ForegroundColor Yellow
Write-Host "1. Open GitHub Desktop" -ForegroundColor White
Write-Host "2. File → Add Local Repository → Browse to: $tempPath" -ForegroundColor White
Write-Host "3. Publish/Push to GitHub" -ForegroundColor White
Write-Host "`nOR create a ZIP file to upload manually" -ForegroundColor Yellow

# Ask if user wants to create ZIP
$createZip = Read-Host "`nDo you want to create a ZIP file? (Y/N)"
if ($createZip -eq "Y" -or $createZip -eq "y") {
    $zipPath = Join-Path $env:USERPROFILE "Desktop\seeding-qdarchive.zip"
    Compress-Archive -Path "$tempPath\*" -DestinationPath $zipPath -Force
    Write-Host "`nZIP file created: $zipPath" -ForegroundColor Green
    Write-Host "You can extract this and push to GitHub" -ForegroundColor Cyan
}

