from typing import Tuple
from dataclasses import dataclass
import logging
from app.hardware import LabJackConnection
from app.exceptions import ValveNotFoundError
from app.config import LABJACK_PINS
from enum import Enum

logger = logging.getLogger(__name__)


class ValveState(str, Enum):
    open = "open"
    closed = "closed"


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
        (1, 1): "center",
        (1, 0): "left",
        (0, 1): "right",
        (0, 0): "moving or stalled",
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

    """

    def __init__(self, labjack: LabJackConnection):
        self.valves = {
            "engine": Valve(LABJACK_PINS["engine_input"], LABJACK_PINS["engine_output"]),
            "relief": Valve(LABJACK_PINS["relief_input"], LABJACK_PINS["relief_output"]),
        }
        self.labjack = labjack

    def _get_valve(self, valve_name: str) -> Valve:
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

    def actuate_valve(self, valve_name: str, state: ValveState) -> str:
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
            self.labjack.write(pin, value)

        return f"Valve {valve_name} is now {state}"

    def get_valve_state(self, valve_name: str) -> str:
        """
        Get the current state of the valve.

        Args:
            valve_name (str): The name of the valve.

        Returns:
            str: The current state of the valve.

        """
        valve = self._get_valve(valve_name)
        output_state = tuple(self.labjack.read(pin)
                             for pin in valve.output_pins)
        feedback = ValveServoState.OUTPUT_STATES[output_state]

        return feedback
