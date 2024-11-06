# Backend Project

This is the backend project for PadStation, built with FastAPI.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)

## Introduction
PadStation is a backend service designed to manage and support the operations of the PadStation application. It provides APIs and handles data processing for the frontend.

## Features
- User authentication and authorization
- Data management and storage
- API endpoints for frontend interaction
- Error handling and logging
- WebSocket support for real-time log streaming

## Installation
To set up the project locally, follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://gitlab.erc.monash.edu.au/Monash-HPR/Control/Firmware/solaris-electronics/pad-station.git
    git checkout Redevelopment
    cd PadStation/backend
    ```

2. **Install dependencies:**
    ```bash
    poetry install
    ```

3. **Set up environment variables:**
    Create a `.env` file in the root directory and add the necessary environment variables.

4. **Configure Poetry to create virtual environment in project directory:**
    ```bash
    poetry config virtualenvs.in-project true
    ```

5. **Run the application:**
    ```bash
    poetry run uvicorn main:app --reload
    ```

6. **Install PM2 globally (if not already installed):**
    ```bash
    npm install -g pm2
    ```

7. **Start the application with PM2:**
    ```bash
    pm2 start ecosystem.config.js
    pm2 save
    ```

## Usage
Once the application is running, you can access the API endpoints at `http://localhost:8000`. Refer to the API documentation for detailed information on available endpoints and their usage.
Additionally, the application supports WebSocket connections for real-time log streaming.
