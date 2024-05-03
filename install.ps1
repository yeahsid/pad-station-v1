# Update package lists for upgrades and new package installations
# No equivalent in Windows, winget automatically fetches the latest packages

# Check if Python is installed, if not, install it
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    winget install --id=Python.Python -e
}

# Check if Poetry is installed, if not, install it
if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
}

# Check if Node.js is installed, if not, install it
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    winget install --id=OpenJS.Nodejs -e
}

# Check if PM2 is installed, if not, install it
if (!(Get-Command pm2 -ErrorAction SilentlyContinue)) {
    npm install -g pm2
}

# Navigate to the backend directory
cd ./backend

# Install Python dependencies with Poetry
poetry install

# Navigate to the frontend directory
cd ../frontend

# Install Node.js dependencies with npm
if (Test-Path -Path package-lock.json) {
    npm ci
} else {
    npm install
}

# Navigate back to the root directory
cd ..

# Start the backend and frontend applications with PM2
pm2 start ecosystem.config.js