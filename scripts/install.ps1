# PowerShell script to set up the project on Windows

# Function to install a package if it's not already installed
function Install-PackageIfNeeded {
    param (
        [string]$packageName
    )
    if (-not (Get-Command $packageName -ErrorAction SilentlyContinue)) {
        Write-Host "Installing $packageName..."
        npm install -g $packageName
    } else {
        Write-Host "$packageName is already installed."
    }
}

# Install Node.js dependencies in frontend
Write-Host "Installing Node.js dependencies in frontend..."
Set-Location -Path "frontend"
npm install
Set-Location -Path ".."

# Install Poetry in backend
Write-Host "Installing Poetry in backend..."
Install-PackageIfNeeded poetry

# Configure Poetry to create virtual environment in project directory
Write-Host "Configuring Poetry to create virtual environment in project directory..."
Set-Location -Path "backend"
poetry config virtualenvs.in-project true

# Install Python dependencies with Poetry in backend
Write-Host "Installing Python dependencies with Poetry in backend..."
poetry install
Set-Location -Path ".."

# Install PM2 globally
Write-Host "Installing PM2 globally..."
Install-PackageIfNeeded pm2

# Start the backend and frontend applications with PM2
Write-Host "Starting applications with PM2..."
pm2 start ecosystem.config.js && pm2 save

Write-Host "Setup complete."