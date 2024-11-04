#!/bin/bash

# Function to install a package if it's not already installed
install_package_if_needed() {
    if ! command -v $1 &> /dev/null
    then
        echo "Installing $1..."
        npm install -g $1
    else
        echo "$1 is already installed."
    fi
}

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Install Python dependencies
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Poetry
echo "Installing Poetry..."
install_package_if_needed poetry

# Install Python dependencies with Poetry
echo "Installing Python dependencies with Poetry..."
poetry install

# Install PM2 globally
echo "Installing PM2 globally..."
install_package_if_needed pm2

# Start the backend and frontend applications with PM2
echo "Starting applications with PM2..."
pm2 start ecosystem.config.js && pm2 save

echo "Setup complete."