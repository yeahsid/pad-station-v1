# PowerShell script to uninstall the project on Windows

# Function to uninstall a package if it's installed
function Uninstall-PackageIfInstalled {
    param (
        [string]$packageName
    )
    if (Get-Command $packageName -ErrorAction SilentlyContinue) {
        Write-Host "Uninstalling $packageName..."
        npm uninstall -g $packageName
    } else {
        Write-Host "$packageName is not installed."
    }
}

# Deactivate and remove Python virtual environment in backend
Write-Host "Removing Python virtual environment in backend..."
Set-Location -Path "backend"
if (Test-Path -Path "venv") {
    try {
        & .\venv\Scripts\deactivate
    } catch {
        Write-Host "Virtual environment is not active."
    }
    Remove-Item -Recurse -Force venv
} else {
    Write-Host "Python virtual environment not found."
}

# Uninstall Poetry in backend
Write-Host "Uninstalling Poetry in backend..."
Uninstall-PackageIfInstalled poetry
Set-Location -Path ".."

# Uninstall PM2 globally
Write-Host "Uninstalling PM2 globally..."
Uninstall-PackageIfInstalled pm2

# Remove Node.js dependencies in frontend
Write-Host "Removing Node.js dependencies in frontend..."
Set-Location -Path "frontend"
if (Test-Path -Path "node_modules") {
    Remove-Item -Recurse -Force node_modules
} else {
    Write-Host "Node.js dependencies not found."
}
Set-Location -Path ".."

# Remove PM2 processes and ecosystem file
Write-Host "Removing PM2 processes and ecosystem file..."
pm2 delete all
pm2 unstartup
Remove-Item -Force $env:USERPROFILE\.pm2\dump.pm2

Write-Host "Uninstallation complete."