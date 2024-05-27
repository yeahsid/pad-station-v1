from collections import deque
from dataclasses import dataclass
import time

import logging
from typing import Tuple
from app.hardware import LabJackConnection
from app.exceptions import MotorError
from app.config import LABJACK_PINS

logger = logging.getLogger(__name__)


@dataclass
class IgnitorRelay:
    """
    Represents a motor with a limit switch.

    Attributes:
        motor_pins (Tuple[str, str]): The pins used to control the motor.
        limit_switch_pin (str): The pin used to detect the limit switch.
    """
    ignitor_pin: str


class IgnitorRelayController:
    """
    The PilotValveController class is responsible for controlling motors with limit switches connected to a LabJack device.

    Args:
        labjack (LabJackConnection): An instance of the LabJackConnection class representing the connection to the LabJack device.

    Attributes:
        motors (dict): A dictionary containing MotorWithLimitSwitch objects, with the motor names as keys and MotorWithLimitSwitch instances as values.
        labjack (LabJackConnection): An instance of the LabJackConnection class representing the connection to the LabJack device.
        last_states (dict): A dictionary to store the last state of each motor.
    """

    def __init__(self, labjack: LabJackConnection):
        self.motors = {
            "ignitor": IgnitorRelay(
                LABJACK_PINS["ignitor_relay_pin"])
        }
        self.labjack = labjack

    def _get_motor(self, motor_name: str) -> IgnitorRelay:
        """
        Retrieves the specified motor.

        Args:
            motor_name (str): The name of the motor.

        Returns:
            MotorWithLimitSwitch: The specified motor.

        Raises:
            MotorNotFoundError: If the specified motor is not found.
        """
        try:
            return self.motors[motor_name]
        except KeyError:
            logger.error("Motor not found")
            raise MotorError("Motor not found")

    def _stop_motor(self, motor_name: str):
        motor = self._get_motor(motor_name)
        self.labjack.write(motor.motor_enable_pin, 0)

    def _spin_close(self, motor_name: str):
        motor = self._get_motor(motor_name)
        self.labjack.write(motor.motor_enable_pin, 1)
        self.labjack.write(motor.motor_in_pins[0], 0)
        self.labjack.write(motor.motor_in_pins[1], 1)

    def _spin_open(self, motor_name: str):
        motor = self._get_motor(motor_name)
        self.labjack.write(motor.motor_enable_pin, 1)
        self.labjack.write(motor.motor_in_pins[0], 1)
        self.labjack.write(motor.motor_in_pins[1], 0)

    def _detect_at_base(self, motor_name: str) -> bool:
        motor = self._get_motor(motor_name)
        return self.labjack.read(motor.limit_switch_base_pin) == 0

    def _detect_at_work(self, motor_name: str) -> bool:
        motor = self._get_motor(motor_name)
        return self.labjack.read(motor.limit_switch_work_pin) == 0

    def open_motor(self, motor_name: str, wait_time: float = 10):
        curr_time = time.time()
        self._spin_open(motor_name)
        while (not (self._detect_at_work(motor_name))) and (time.time() - curr_time < wait_time):
            pass
        self._stop_motor(motor_name)

    def close_motor(self, motor_name: str, wait_time: float = 10):
        curr_time = time.time()
        self._spin_close(motor_name)
        while (not self._detect_at_base(motor_name)) and (time.time() - curr_time < wait_time):
            pass
        self._stop_motor(motor_name)

    def actuate_valve(self, motor_name: str, state: str):
        if state == "open":
            self.open_motor(motor_name)
        elif state == "close":
            self.close_motor(motor_name)
        else:
            raise MotorError("Invalid state")
        return state
