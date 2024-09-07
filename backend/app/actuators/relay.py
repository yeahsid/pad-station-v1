from collections import deque
from dataclasses import dataclass
import time

import logging
from typing import Tuple
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import MotorError
from app.config import LABJACK_PINS
import asyncio

import csv

logger = logging.getLogger(__name__)


@dataclass
class IgnitorRelay:
    """
    Represents an ignitor relay.

    Attributes:
        ignitor_pin (str): The pin number for the ignitor relay.
    """
    ignitor_pin: str


class IgnitorRelayController:
    """
    Represents an ignitor relay controller that controls the ignitor relay using LabJackConnection.

    Attributes:
        relays (dict): A dictionary of relays, where the keys are the names of the relays
            and the values are instances of the IgnitorRelay class.
        labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.

    """

    def __init__(self, labjack: LabJackConnection):
        self.relays = {
            "ignitor": IgnitorRelay(
                LABJACK_PINS["ignitor_relay_pin"]),
            "vent": IgnitorRelay(
                LABJACK_PINS["vent_relay_pin"]),
            "qd": IgnitorRelay(
                LABJACK_PINS["qd_relay_pin"])
        }
        self.labjack = labjack

    def _get_relay(self, relay_name: str) -> IgnitorRelay:
        """
        Retrieves the specified relay.

        Args:
            relay_name (str): The name of the relay.
        
        Returns:
            IgnitorRelay: The specified relay.

        Raises:
            MotorError: If the specified relay is not found.
        """
        try:
            return self.relays[relay_name]
        except KeyError:
            logger.error("Motor not found")
            raise MotorError("Motor not found")

    async def actuate_relay(self, relay_name):
        relay = self._get_relay(relay_name)
        await self.labjack.write(relay.ignitor_pin, 1)
        await asyncio.sleep(1)
        await self.labjack.write(relay.ignitor_pin, 0)
        return 
