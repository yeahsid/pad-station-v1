"""
This Python module, models.py, contains a Pydantic model for the response for HTTP requests to the backend server.
The ValveResponse model has two fields: valve_name and feedback. The valve_name field is a required string that represents the name of the valve. 
The feedback field is an optional string that represents the feedback from the valve operation. 
If there's no feedback, feedback can be None.
"""

# Import necessary modules
from pydantic import BaseModel
from typing import Optional

# Define a Pydantic model for the response of a valve operation


class ValveResponse(BaseModel):
    """
    Represents the response from a valve operation.

    Attributes:
        valve_name (str): The name of the valve.
        feedback (Optional[str]): The feedback from the valve operation, can be None.
    """
    valve_name: str
    feedback: Optional[str]


class PressureResponse(BaseModel):
    """
    Represents the response from a pressure sensor reading.

    Attributes:
        sensor_name (str): The name of the pressure sensor.
        pressure (float): The pressure reading from the sensor.
    """
    sensor_name: str
    pressure: float


class MotorControllerHealthResponse(BaseModel):
    """
    Represents the response from a motor controller health check on RS422 .

    Attributes:
        controller_name (str): The name of the motor controller.
        status (str): The status of the motor controller.
    """
    controller_name: str
    status: str

class MotorControllerHeartbeat(BaseModel):
    """
    Represents the response from a motor controller heartbeat on RS422 .

    Attributes:
        controller_name (str): The name of the motor controller.
        status (str): The status of the motor controller.
    """
    controller_name: str
    status: str
