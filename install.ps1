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

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..."
npm install

# Install Python dependencies
Write-Host "Setting up Python virtual environment..."
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Install Poetry
Write-Host "Installing Poetry..."
Install-PackageIfNeeded poetry

# Install Python dependencies with Poetry
Write-Host "Installing Python dependencies with Poetry..."
poetry install

# Install PM2 globally
Write-Host "Installing PM2 globally..."
Install-PackageIfNeeded pm2

# Start the backend and frontend applications with PM2
Write-Host "Starting applications with PM2..."
pm2 start ecosystem.config.js && pm2 save

Write-Host "Setup complete."