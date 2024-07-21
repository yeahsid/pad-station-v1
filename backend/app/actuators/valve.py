from typing import Tuple
from dataclasses import dataclass
import logging
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import ValveNotFoundError
from app.config import LABJACK_PINS
from enum import Enum

logger = logging.getLogger(__name__)


class ValveState(str, Enum):
    open = "open"
    closed = "closed"
    error = "error"


class ValveServoState:
    INPUT_STATES = {
        "engine": {
            ValveState.open: (1, 0),
            ValveState.closed: (1, 1),
        },
        "relief": {
            ValveState.open: (1, 1),
            ValveState.closed: (1, 0),
        },
    }
    OUTPUT_STATES = {
        (1, 1): ValveState.closed,
        (1, 0): ValveState.open,
        (0, 1): ValveState.error,
        (0, 0): ValveState.error,
    }


@dataclass
class Valve:
    input_pins: Tuple[str, str]
    output_pins: Tuple[str, str]


class ValveController:
    """
    The ValveController class is responsible for controlling valves connected to a LabJack device.

    Args:
        labjack (LabJackConnection): An instance of the LabJackConnection class representing the connection to the LabJack device.

    Attributes:
        valves (dict): A dictionary containing Valve objects, with the valve names as keys and Valve instances as values.
        labjack (LabJackConnection): An instance of the LabJackConnection class representing the connection to the LabJack device.
        last_states (dict): A dictionary to store the last state of each valve.

    """

    def __init__(self, labjack: LabJackConnection):
        self.valves = {
            "engine": Valve(LABJACK_PINS["engine_input"], LABJACK_PINS["engine_output"]),
            "relief": Valve(LABJACK_PINS["relief_input"], LABJACK_PINS["relief_output"]),
        }
        self.labjack = labjack
        self.last_states = {}

    async def _get_valve(self, valve_name: str) -> Valve:
        """
        Get the Valve instance corresponding to the given valve name.

        Args:
            valve_name (str): The name of the valve.

        Returns:
            Valve: The Valve instance corresponding to the given valve name.

        Raises:
            ValveNotFoundError: If the valve with the given name is not found.

        """
        if valve_name not in self.valves:
            logger.error("Valve not found")
            raise ValveNotFoundError("Valve not found")
        return self.valves[valve_name]

    async def actuate_valve(self, valve_name: str, state: ValveState) -> str:
        """
        Actuate the valve to the specified state.

        Args:
            valve_name (str): The name of the valve.
            state (ValveState): The desired state of the valve.

        Returns:
            str: A message indicating the current state of the valve.

        """
        valve = self._get_valve(valve_name)
        input_state = ValveServoState.INPUT_STATES[valve_name][state]

        for pin, value in zip(valve.input_pins, input_state):
            await self.labjack.write(pin, value)

        # Store the last actuated state
        self.last_states[valve_name] = state

    async def get_valve_state(self, valve_name: str) -> str:
        """
        Get the last actuated state of the valve.

        Args:
            valve_name (str): The name of the valve.

        Returns:
            str: The last actuated state of the valve.

        Raises:
            ValveNotFoundError: If the valve with the given name is not found.

        """
        if valve_name not in self.last_states:
            logger.error("Valve not found")
            raise ValveNotFoundError("Valve not found")
        return self.last_states[valve_name]
