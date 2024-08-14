from collections import deque
from dataclasses import dataclass
import time

import logging
from typing import Tuple
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import MotorError
from app.config import LABJACK_PINS
import csv
logger = logging.getLogger(__name__)
import asyncio


@dataclass
class PilotValve:
    """
    Represents a motor with a limit switch.

    Attributes:
        motor_pins (Tuple[str, str]): The pins used to control the motor.
        limit_switch_pin (str): The pin used to detect the limit switch.
    """
    motor_enable_pin: str
    motor_in_pins: Tuple[str, str]
    limit_switch_base_pin: str
    limit_switch_work_pin: str
    ignitor_relay_pin: str


class PilotValveController:
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
            "pilot_valve": PilotValve(
                LABJACK_PINS["pilot_valve_motor_enable"],
                (LABJACK_PINS["pilot_valve_motor_in_1"],
                 LABJACK_PINS["pilot_valve_motor_in_2"]),
                LABJACK_PINS["pilot_valve_limit_switch_base"],
                LABJACK_PINS["pilot_valve_limit_switch_work"],
                LABJACK_PINS["ignitor_relay_pin"])
        }
        self.labjack = labjack

    def _get_motor(self, motor_name: str) -> PilotValve:
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

    async def _stop_motor(self, motor_name: str):
        motor = self._get_motor(motor_name)
        await self.labjack.write(motor.motor_enable_pin, 0)

    async def _spin_close(self, motor_name: str):
        motor = self._get_motor(motor_name)
        await self.labjack.write(motor.motor_enable_pin, 1)
        await self.labjack.write(motor.motor_in_pins[0], 0)
        await self.labjack.write(motor.motor_in_pins[1], 1)

    async def _spin_open(self, motor_name: str):
        motor = self._get_motor(motor_name)
        await self.labjack.write(motor.motor_enable_pin, 1)
        await self.labjack.write(motor.motor_in_pins[0], 1)
        await self.labjack.write(motor.motor_in_pins[1], 0)

    async def _detect_at_base(self, motor_name: str) -> bool:
        motor = self._get_motor(motor_name)
        while True:
            if await self.labjack.read(motor.limit_switch_base_pin) == 1:
                return True
            await asyncio.sleep(0.01)

    async def _detect_at_work(self, motor_name: str) -> bool:
        motor = self._get_motor(motor_name)
        while True:
            if await self.labjack.read(motor.limit_switch_work_pin) == 1:
                return True
            await asyncio.sleep(0.01)

    async def open_motor(self, motor_name: str, wait_time: int = 15):
        await self._spin_open(motor_name)
        try:
            await asyncio.wait_for(self._detect_at_base(motor_name), timeout=wait_time)
            print(await self.labjack.read(self._get_motor(motor_name).limit_switch_work_pin))
        except asyncio.TimeoutError:
            pass
        await self._stop_motor(motor_name)

    async def close_motor(self, motor_name: str, wait_time: int = 15):
        await self._spin_close(motor_name)
        try:
            await asyncio.wait_for(self._detect_at_work(motor_name), timeout=wait_time)
        except asyncio.TimeoutError:
            pass
        await self._stop_motor(motor_name)

    async def actuate_valve(self, motor_name: str, state: str, timeout: int):
        if state == "open":
            await self.open_motor(motor_name, timeout)
        elif state == "closed":
            await self.close_motor(motor_name, timeout)
        else:
            raise MotorError(f"Invalid state: {state}")
        return state

    async def actuate_ignitor(self, valve_name, delay):
        await self.labjack.write(LABJACK_PINS["ignitor_relay_pin"], 1)
        
        await asyncio.sleep(delay)

        await self.open_motor(valve_name)
        await self.labjack.write(LABJACK_PINS["ignitor_relay_pin"], 0)
        return "Ignitor actuated"
