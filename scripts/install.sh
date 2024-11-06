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

# Install Node.js dependencies in frontend
echo "Installing Node.js dependencies in frontend..."
cd frontend
npm install
cd ..

# Install Poetry in backend
echo "Installing Poetry in backend..."
install_package_if_needed poetry

# Configure Poetry to create virtual environment in project directory
echo "Configuring Poetry to create virtual environment in project directory..."
cd backend
poetry config virtualenvs.in-project true

# Install Python dependencies with Poetry in backend
echo "Installing Python dependencies with Poetry in backend..."
poetry install
cd ..

# Install PM2 globally
echo "Installing PM2 globally..."
install_package_if_needed pm2

# Start the backend and frontend applications with PM2
echo "Starting applications with PM2..."
pm2 start ecosystem.config.js && pm2 save

echo "Setup complete."