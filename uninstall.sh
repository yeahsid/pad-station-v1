#!/bin/bash

# Function to uninstall a package if it's installed
uninstall_package_if_installed() {
    if command -v $1 &> /dev/null
    then
        echo "Uninstalling $1..."
        npm uninstall -g $1
    else
        echo "$1 is not installed."
    fi
}

# Deactivate and remove Python virtual environment
echo "Removing Python virtual environment..."
if [ -d "venv" ]; then
    deactivate 2>/dev/null
    rm -rf venv
else
    echo "Python virtual environment not found."
fi

# Uninstall Poetry
echo "Uninstalling Poetry..."
uninstall_package_if_installed poetry

# Uninstall PM2 globally
echo "Uninstalling PM2 globally..."
uninstall_package_if_installed pm2

# Remove Node.js dependencies
echo "Removing Node.js dependencies..."
if [ -d "node_modules" ]; then
    rm -rf node_modules
else
    echo "Node.js dependencies not found."
fi

# Remove PM2 processes and ecosystem file
echo "Removing PM2 processes and ecosystem file..."
pm2 delete all
pm2 unstartup
rm -f ~/.pm2/dump.pm2

echo "Uninstallation complete."