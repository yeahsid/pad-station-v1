from dataclasses import dataclass
import asyncio

import logging
from app.hardware import LabJackConnection
from app.exceptions import PressureSensorError
from app.config import LABJACK_PINS

logger = logging.getLogger(__name__)


@dataclass
class PressureTransducer:
    pressure_signal: str
    max_pressure: float  # The maximum pressure the transducer can measure


class PressureTransducerSensor:
    """
    Represents a pressure transducer sensor that measures pressure using LabJackConnection.

    Attributes:
        pressure_transducers (dict): A dictionary of pressure transducers, where the keys are the names of the transducers
            and the values are instances of the PressureTransducer class.
        labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
    """

    def __init__(self, labjack: LabJackConnection):
        """
        Initializes a PressureTransducerSensor object.

        Args:
            labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
        """
        self.pressure_transducers = {
            # Assuming max pressure is 100
            "supply": PressureTransducer(LABJACK_PINS["pressure_transducer_supply"], 200),
            # Assuming max pressure is 100
            "engine": PressureTransducer(LABJACK_PINS["pressure_transducer_engine"], 200),
        }
        self.labjack = labjack

    def _get_pressure_transducer(self, pressure_transducer_name: str) -> PressureTransducer:
        """
        Retrieves the specified pressure transducer.

        Args:
            pressure_transducer_name (str): The name of the pressure transducer.

        Returns:
            PressureTransducer: The specified pressure transducer.

        Raises:
            PressureSensorError: If the specified pressure transducer is not found.
        """
        try:
            return self.pressure_transducers[pressure_transducer_name]
        except KeyError:
            logger.error("Pressure Transducer not found")
            raise PressureSensorError("Pressure Transducer not found")

    def get_pressure_transducer_feedback(self, pressure_transducer_name: str) -> float:
        """
        Gets the pressure transducer feedback for the specified pressure transducer.

        Args:
            pressure_transducer_name (str): The name of the pressure transducer.

        Returns:
            float: The pressure transducer feedback in units of pressure.

        """
        pressure_transducer = self._get_pressure_transducer(
            pressure_transducer_name)
        voltage = self.labjack.read(pressure_transducer.pressure_signal)
        return (voltage - 0.5) / 4 * pressure_transducer.max_pressure

    async def pressure_transducer_datastream(self, pressure_transducer_name: str):
        """
        Creates a data stream of pressure readings from the specified pressure transducer.

        Args:
            pressure_transducer_name (str): The name of the pressure transducer.

        Yields:
            float: The next pressure reading from the specified pressure transducer.
        """
        while True:
            yield self.get_pressure_transducer_feedback(pressure_transducer_name)
            await asyncio.sleep(0)  # Yield control to the event loop
