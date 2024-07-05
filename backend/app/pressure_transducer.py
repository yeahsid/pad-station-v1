from collections import deque
from dataclasses import dataclass
import asyncio
from datetime import datetime
import logging
from app.hardware import LabJackConnection
from app.exceptions import PressureSensorError
from app.config import LABJACK_PINS
import aiofiles
import csv

LOGGING_RATE = 1  # Time between pt log points in seconds

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
            "tank_bottom": PressureTransducer(LABJACK_PINS["pressure_transducer_engine"], 200),
            "tank_top": PressureTransducer(LABJACK_PINS["pressure_transducer_tank"], 200),
            "chamber": PressureTransducer(LABJACK_PINS["pressure_transducer_chamber"], 200),
        }
        self.labjack = labjack
        self.filter_size = filter_size
        self.pressure_readings = {name: deque(
            maxlen=filter_size) for name in self.pressure_transducers}
        self.pressure_sums = {name: 0 for name in self.pressure_transducers}

        self.logging_active = True  # Used to disable logging at a chosen time

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
            logger.error(f"Pressure Transducer with name {pressure_transducer_name} not found")
            raise PressureSensorError(f"Pressure Transducer with name {pressure_transducer_name} not found")

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
        while True:
            pressure_reading, voltage = self.get_pressure_transducer_feedback(pressure_transducer_name)
            yield pressure_reading
            await asyncio.sleep(LOGGING_RATE)  # Adjust the sleep time as needed

    async def pressure_transducer_logging(self, pressure_transducer_name: str):
        filename = f'/home/padstation/pad-station/logs/pressure/{pressure_transducer_name}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'

        async with aiofiles.open(filename, 'w', newline='') as file:
            await file.write("Pressure Reading,Voltage,Time\n")

            while self.logging_active:
                pressure_reading, voltage = self.get_pressure_transducer_feedback(pressure_transducer_name)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                await file.write(f"{pressure_reading},{voltage},{current_time}\n")
                await asyncio.sleep(LOGGING_RATE)  # Adjust as needed

    async def start_logging_all_sensors(self):
        self.logging_active = True
        tasks = [self.pressure_transducer_logging(name) for name in self.pressure_transducers]
        await asyncio.gather(*tasks)

    def end_logging_all_sensors(self):
        self.logging_active = False


