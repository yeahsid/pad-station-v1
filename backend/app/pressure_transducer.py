from collections import deque
from dataclasses import dataclass
import asyncio
import time

import logging
from app.hardware import LabJackConnection
from app.exceptions import PressureSensorError
from app.config import LABJACK_PINS
import csv

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

    def __init__(self, labjack: LabJackConnection, filter_size: int = 10):
        """
        Initializes a PressureTransducerSensor object.

        Args:
            labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
        """
        self.pressure_transducers = {
            "supply": PressureTransducer(LABJACK_PINS["pressure_transducer_supply"], 200),
            "engine": PressureTransducer(LABJACK_PINS["pressure_transducer_engine"], 200),
            "tank": PressureTransducer(LABJACK_PINS["pressure_transducer_tank"], 200),
            "chamber": PressureTransducer(LABJACK_PINS["pressure_transducer_chamber"], 200),

        }
        self.labjack = labjack
        self.filter_size = filter_size
        self.pressure_readings = {name: deque(
            maxlen=filter_size) for name in self.pressure_transducers}
        self.pressure_sums = {name: 0 for name in self.pressure_transducers}

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
        pressure_transducer = self._get_pressure_transducer(
            pressure_transducer_name)
        voltage = self.labjack.read(pressure_transducer.pressure_signal)
        # Calculate pressure from voltage
        pressure = (voltage - 0.5) / 4 * pressure_transducer.max_pressure
        # pressure_bar = pressure_psi * 0.0689476  # Convert pressure from PSI to bar
        return round(pressure, 2), voltage

    async def pressure_transducer_datastream(self, pressure_transducer_name: str):
        """
        Creates a data stream of pressure readings from the specified pressure transducer.

        Args:
            pressure_transducer_name (str): The name of the pressure transducer.

        Yields:
            float: The next pressure reading from the specified pressure transducer.

        """
        with open(f'.././logs/pressure/{pressure_transducer_name}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Pressure Reading"] + ["Voltage"] + ["Time"])
            while True:
                pressure_reading, voltage = self.get_pressure_transducer_feedback(
                    pressure_transducer_name)
                writer.writerow([pressure_reading] +
                                [voltage] + [time.time()])
                yield pressure_reading
