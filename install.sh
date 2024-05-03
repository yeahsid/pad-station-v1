#!/bin/bash

# Update package lists for upgrades and new package installations
sudo apt-get update

# Check if Python is installed, if not, install it
if ! command -v python3 &> /dev/null
then
    sudo apt-get install -y python3 python3-pip
fi

# Check if Poetry is installed, if not, install it
if ! command -v poetry &> /dev/null
then
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Check if Node.js is installed, if not, install it
if ! command -v node &> /dev/null
then
    curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Check if PM2 is installed, if not, install it
if ! command -v pm2 &> /dev/null
then
    sudo npm install -g pm2
fi


# Install Python dependencies with Poetry
poetry install

# Navigate to the frontend directory
cd ./frontend

# Install Node.js dependencies with npm
if [ -f package-lock.json ]; then
    npm ci
else
    npm install
fi

# Navigate back to the root directory
cd ..

# Start the backend and frontend applications with PM2
pm2 start ecosystem.config.js