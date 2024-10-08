from typing import Tuple
from dataclasses import dataclass
import logging
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import ServoNotFoundError
from app.config import LABJACK_PINS
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

ACTIVE_VENT_CLOSED = 89000 # RICKY CHANGE THIS
ACTIVE_VENT_OPEN = 111000 # RICKY CHANGE THIS

class ServoState(str, Enum):
    open = "open"
    closed = "closed"

@dataclass
class Servo:
    """
    Represents a servo motor.

    Attributes:
        control_pin (str): The pin used to control the servo.
        open_position (int): The position value for the open state.
        closed_position (int): The position value for the closed state.
    """
    control_pin: str
    power_relay_pin: str
    open_position: int
    closed_position: int

class ServoController:
    """
    The ServoController class is responsible for controlling servos connected to a LabJack device.

    Args:
        labjack (LabJackConnection): An instance of the LabJackConnection class representing the connection to the LabJack device.

    Attributes:
        servos (dict): A dictionary containing Servo objects, with the servo names as keys and Servo instances as values.
        labjack (LabJackConnection): An instance of the LabJackConnection class representing the connection to the LabJack device.
        servo_setup_status (dict): A dictionary to track the setup status of each servo.
    """

    def __init__(self, labjack: LabJackConnection):
        self.servos = {
            "active_vent": Servo(
                LABJACK_PINS["active_vent_servo_pwm"],
                LABJACK_PINS["active_vent_relay_pin"],
                ACTIVE_VENT_OPEN,
                ACTIVE_VENT_CLOSED
            )
        }
        self.labjack = labjack
        self.servo_setup_status = {}

    def _get_servo(self, servo_name: str) -> Servo:
        """
        Get the Servo instance corresponding to the given servo name.

        Args:
            servo_name (str): The name of the servo.

        Returns:
            Servo: The Servo instance corresponding to the given servo name.

        Raises:
            ServoNotFoundError: If the servo with the given name is not found.
        """
        if servo_name not in self.servos:
            logger.error("Servo not found")
            raise ServoNotFoundError("Servo not found")
        return self.servos[servo_name]

    async def _servo_setup(self, servo_name: str):
        """
        Sets up the LabJack device to control the specified servo.

        Args:
            servo_name (str): The name of the servo.
        """
        servo = self._get_servo(servo_name)

        # Configure PWM Functionality
        # Configure Clock Registers:
        await self.labjack.write("DIO_EF_CLOCK0_ENABLE", 0)
        # Disable clock source

        # Set Clock0's divisor and roll value to configure frequency:
        # 80MHz/1/1,000,000 = 80Hz (within the 50-330Hz range of servo)
        await self.labjack.write("DIO_EF_CLOCK0_DIVISOR", 1)
        # Configure Clock0's divisor
        await self.labjack.write("DIO_EF_CLOCK0_ROLL_VALUE", 1000000)
        # Configure Clock0's roll value to get 80Hz
        await self.labjack.write("DIO_EF_CLOCK0_ENABLE", 1)
        # Enable the clock source

        # Configure EF Channel Registers:
        await self.labjack.write(f"{servo.control_pin}_EF_ENABLE", 0)
        # Disable the EF system for initial configuration
        await self.labjack.write(f"{servo.control_pin}_EF_INDEX", 0)
        # Configure EF system for PWM
        await self.labjack.write(f"{servo.control_pin}_EF_OPTIONS", 0)
        # Configure what clock source to use: Clock0

        await self.labjack.write(f"{servo.control_pin}_EF_CONFIG_A", servo.open_position)
        # Set startup position to be in middle
        await self.labjack.write(f"{servo.control_pin}_EF_ENABLE", 1)
        # Enable the EF system after completing configuration

        await self.labjack.write(servo.power_relay_pin, 1)

        self.servo_setup_status[servo_name] = True

    async def actuate_servo(self, servo_name: str, state: ServoState) -> str:
        """
        Actuate the servo to the specified state.

        Args:
            servo_name (str): The name of the servo.
            state (ServoState): The desired state of the servo.

        Returns:
            str: A message indicating the current state of the servo.
        """
        servo = self._get_servo(servo_name)
        if not self.servo_setup_status.get(servo_name, False):
            await self._servo_setup(servo_name)

        position = servo.open_position if state == ServoState.open else servo.closed_position
        await self.labjack.write(f"{servo.control_pin}_EF_CONFIG_A", position)
        print("position: ", position)

        return f"Servo {servo_name} actuated to {state}"