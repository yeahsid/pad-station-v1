#!/bin/bash

# Install Python dependencies with Poetry
poetry install

# Navigate to the frontend directory
cd ../frontend

# Install Node.js dependencies with npm
npm install

# Navigate back to the root directory
cd ..

# Start the backend and frontend applications with PM2
pm2 start ecosystem.config.js