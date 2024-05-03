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
install_packages python3 python3-pip python3-virtualenv , pipx

pipx ensurepath


# Install nodejs with NVM.

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

nvm install node

source ~/.bashrc

# Install Poetry with pipx
if ! command -v poetry &> /dev/null; then
    pipx install poetry
fi



# Navigate to the backend directory and install Python dependencies with Poetry
cd ./backend && poetry install

npm install -g pm2

# Navigate to the frontend directory and install Node.js dependencies with npm
cd ../frontend && ( [ -f package-lock.json ] && npm ci || npm install )

