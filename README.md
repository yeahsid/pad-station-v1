# Pad Station Documentation

This document provides an overview of the Pad Station API, a FastAPI application designed to control and monitor the status of valves, sensors, and servos connected to a LabJack device.

## Setting Up

Follow these steps to install the application:

1. Clone the repository to your local machine.
2. Depending on your operating system, run the appropriate installation script:
   - For Unix/macOS: `./install.sh`
   - For Windows: `.\install.ps1`

These scripts will install the necessary dependencies for the application.

## How to Use

To start the server, use the following command:

```bash
pm2 start ecosystem.config.js
```

The API provides several endpoints:

- `GET /valve/{valve_name}`: Controls a valve. The desired state of the valve (either open or closed) should be provided in the request body.
- `GET /valve/{valve_name}/state`: Retrieves the current state of a specific valve.
- `GET /pressure/{pressure_transducer_name}/feedback`: Retrieves the raw feedback from a specific pressure transducer.
- `GET /pressure/{pressure_transducer_name}/datastream`: Retrieves a stream of processed data from a specific pressure transducer.

## Required Libraries

This application relies on several Python libraries:

- FastAPI: Used to build the API.
- Pydantic: Handles data validation and serialization.
- LabJackPython: Facilitates interaction with the LabJack device.

## Code Structure

The application's codebase is organized as follows:

- `main.py`: This is the application's entry point. It initializes the FastAPI application and defines the routes.
- `hardware.py`: This file contains the `LabJackConnection` class, which manages the connection to the LabJack device.
- `valve.py`: This file includes classes for controlling valves and retrieving their states.
- `models.py`: This file defines Pydantic models for the data used in requests and responses.
- `exceptions.py`: This file defines custom exceptions for the application.
- `config.py`: This file contains the application's configuration variables.
- `servo.py` : This file includes classes for controlling servos and retrieving their feedback.

## Handling Errors

The application has custom exception handlers for `DeviceNotOpenError`, `ValveNotFoundError`, `ServoNotFoundError`, and `LabJackError`. If these exceptions are raised, the application responds with a 500 status code and a message that describes the error.

## Logging

The application logs all request and response details, as well as any errors that occur. These logs are displayed in the console and can be configured to be saved in a log file.
