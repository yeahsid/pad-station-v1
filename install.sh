#!/bin/bash

# Define a function to install a package
install_package() {
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y "$1"
    elif command -v yum &> /dev/null; then
        sudo yum install -y "$1"
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y "$1"
    elif command -v brew &> /dev/null; then
        brew install "$1"
    else
        echo "No known package manager found" >&2
        exit 1
    fi
}

# Update package lists for upgrades and new package installations
update_packages() {
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
    elif command -v yum &> /dev/null; then
        sudo yum check-update
    elif command -v dnf &> /dev/null; then
        sudo dnf check-update
    elif command -v brew &> /dev/null; then
        brew update
    fi
}

# Install a list of packages
install_packages() {
    for package in "$@"; do
        if ! command -v "$package" &> /dev/null; then
            install_package "$package"
        fi
    done
}

# Update packages
update_packages

# Install Python, pip, Node.js
install_packages python3 python3-pip node  python3-virtualenv

# Install pipx
if ! command -v pipx &> /dev/null; then
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    # Refresh the PATH
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install Poetry with pipx
if ! command -v poetry &> /dev/null; then
    pipx install poetry
fi

# Navigate to the backend directory and install Python dependencies with Poetry
cd ./backend && poetry install

# Navigate to the frontend directory and install Node.js dependencies with npm
cd ../frontend && ( [ -f package-lock.json ] && npm ci || npm install )

# Use npx to install PM2
npx pm2
