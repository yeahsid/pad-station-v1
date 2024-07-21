from collections import deque
from dataclasses import dataclass
import asyncio
import time
import logging
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import LoadCellError
from app.config import LABJACK_PINS
import csv
import aiofiles
from datetime import datetime, timezone
LOGGING_RATE = 0.005  # Time between pt log points in seconds

logger = logging.getLogger(__name__)

@dataclass
class LoadCell:
    signal_pos: str
    signal_neg: str
    calibration_factor: float
    calibration_constant: float

class LoadCellSensor:
    """
    A class that represents Load Cells using a LabJackConnection.

    Attributes:
        load_cells (dict): A dictionary of load cells with load cell names as keys and LoadCell objects as values.
        labjack (LabJackConnection): An instance of LabJackConnection used for communication with the LabJack device.
    """
    def __init__(self, labjack: LabJackConnection):
        """
        Initializes a LoadCellController object.

        Args:
            labjack (LabJackConnection): An instance of LabJackConnection used for communication with the LabJack device.
        """
        self.load_cells = {
            # "test_stand": LoadCell(*LABJACK_PINS["test_stand_load_cell"], -30606.38127, 1.00271157)

            "test_stand": LoadCell( "AIN8", "AIN9", -30606.38127, 1.00271157)
        }
        self.labjack = labjack

    def _get_load_cell(self, load_cell_name: str) -> LoadCell:
        """
        Retrieves a LoadCell object based on the load cell name.

        Args:
            load_cell_name (str): The name of the load cell.

        Returns:
            LoadCell: The LoadCell object.

        Raises:
            LoadCellError: If the load cell with the specified name is not found.
        """
        try:
            return self.load_cells[load_cell_name]
        except KeyError:
            logger.error("Load cell not found")
            raise LoadCellError("Load cell not found")

    def get_load_cell_mass(self, load_cell_name: str) -> float:
        """
        Retrieves the mass value from a load cell.

        Args:
            load_cell_name (str): The name of the load cell.

        Returns:
            float: The mass value from the load cell.
        """
        load_cell = self._get_load_cell(load_cell_name)
        
        self.labjack.write(f"{load_cell.signal_pos}_RANGE", 0.01)
        self.labjack.write(f"{load_cell.signal_pos}_RESOLUTION_INDEX", 0)
        self.labjack.write(f"{load_cell.signal_neg}_NEGATIVE_CH", int(load_cell.signal_neg[3:]))
        self.labjack.write(f"{load_cell.signal_pos}_SETTLING_US", 0)

        voltage_value = self.labjack.read(load_cell.signal_pos)

        load = voltage_value * load_cell.calibration_factor + load_cell.calibration_constant

        return load , voltage_value

    async def load_cell_datastream(self, load_cell_name: str):
        """
        Creates a data stream of mass readings from the specified load cell.

        Args:
            load_cell_name (str): The name of the load cell.

        Yields:
            float: The next mass reading from the specified load cell.
        """
        while True:
            load = self.get_load_cell_mass(load_cell_name)
            yield load
            await asyncio.sleep(LOGGING_RATE)  # Adjust the sleep time as needed

    async def load_cell_logging(self, load_cell_name: str):
        filename = f'/home/padstation/pad-station/logs/load_cell/{load_cell_name}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'

        async with aiofiles.open(filename, 'w', newline='') as file:
            await file.write("Load,Voltage,Time\n")

            while self.logging_active:
                load, voltage = self.get_load_cell_mass(load_cell_name)
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                await file.write(f"{load},{voltage},{current_time}\n")
                await asyncio.sleep(LOGGING_RATE)
                await file.flush()

    async def start_logging_all_sensors(self):
        self.logging_active = True
        tasks = [self.load_cell_logging(name) for name in self.load_cells]
        await asyncio.gather(*tasks)

    def end_logging_all_sensors(self):
        self.logging_active = False