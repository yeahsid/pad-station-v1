from collections import deque
from dataclasses import dataclass
import asyncio
from datetime import datetime, timezone
import logging
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import LoadCellError
from app.config import LABJACK_PINS
import aiofiles
import redis
from concurrent.futures import ThreadPoolExecutor


import csv
import os
from pathlib import Path

LOGGING_RATE = 0.0001  # Time between tc log points in seconds
POLLING_RATE = 0.5 # Time between tc readings in seconds

logger = logging.getLogger(__name__)


@dataclass
class load_cell:
    signal_pos: str
    signal_neg: str
    calibration_factor: float
    calibration_constant: float


class LoadCellSensor:
    """
    Represents a load_cell sensor that measures force using LabJackConnection.

    Attributes:
        load_cells (dict): A dictionary of load_cells, where the keys are the names of the load_cells
            and the values are instances of the load_cell class.
        labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
    """

    def __init__(self, labjack: LabJackConnection, filter_size: int = 10):
        """
        Initializes a load_cellSensor object.

        Args:
            labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
        """
        self.load_cells = {
            "test_stand": load_cell(*LABJACK_PINS["load_cell"] , 1214127 , 34.6), # 7629, -3017
            "rail_mass": load_cell(*LABJACK_PINS["load_cell"] , 12422.3602484472 , 1.166149068)
        }
        self.labjack = labjack

        self.load_cell_setup = False

        self.logging_active = False

    def _get_load_cell(self, load_cell_name: str) -> load_cell:
        """
        Retrieves the specified load_cell.

        Args:
            load_cell_name (str): The name of the load_cell.

        Returns:
            load_cell: The specified load_cell.

        Raises:
            load_cellSensorError: If the specified load_cell is not found.
        """
        try:
            return self.load_cells[load_cell_name]
        except KeyError:
            logger.error("load_cell not found")
            raise LoadCellError("load_cell not found")
        

    async def _load_cell_setup(self, load_cell_name: str):
        """
        Sets up the LabJack device to read from the specified load_cell.

        Args:
            load_cell_name (str): The name of the load_cell.
        """
        load_cell = self._get_load_cell(load_cell_name)

        # Set up the load_cell
        await self.labjack.write(f"{load_cell.signal_pos}_RANGE", 0.01)
        await self.labjack.write(f"{load_cell.signal_pos}_RESOLUTION_INDEX", 0)
        await self.labjack.write(f"{load_cell.signal_pos}_NEGATIVE_CH", int(load_cell.signal_neg[-1]))
        await self.labjack.write(f"{load_cell.signal_pos}_SETTLING_US", 0)
        self.load_cell_setup = True 

    async def get_load_cell_force(self, load_cell_name: str) -> float:
        """
        Get the force reading from a load_cell.

        Args:
            load_cell_name (str): The name of the load_cell.

        Returns:
            float: The force reading in degrees N.
        """
        load_cell = self._get_load_cell(load_cell_name)
        if not self.load_cell_setup:
            await self._load_cell_setup(load_cell_name)
            

        voltage = await self.labjack.read(load_cell.signal_pos) 
        force = voltage * load_cell.calibration_factor + load_cell.calibration_constant


        return round(force, 3)

    async def load_cell_datastream(self, load_cell_name: str):
        """
        Creates a data stream of force readings from the specified load_cell.

        Args:
            load_cell_name (str): The name of the load_cell.

        Yields:
            float: The next force reading from the specified load_cell.
        """

        while True:
            force = await self.get_load_cell_force(load_cell_name)
            yield force
            await asyncio.sleep(POLLING_RATE)
    
    async def load_cell_logging(self, load_cell_name: str):
        # Initialize Redis connection
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Create a ThreadPoolExecutor
        executor = ThreadPoolExecutor()
        redis_client.delete(f"load_data:{load_cell_name}")
        try:
            while self.logging_active:
                force_reading = await self.get_load_cell_force(load_cell_name)
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                
                # Create a structured string or a dictionary to represent the data
                data = f"{force_reading},{current_time}"
                
                # Use run_in_executor to run the synchronous Redis operation in a separate thread
                await asyncio.get_event_loop().run_in_executor(executor, lambda: redis_client.lpush(f"load_data:{load_cell_name}", data))
                
                await asyncio.sleep(LOGGING_RATE)
        finally:
            # Close Redis connection outside of the loop
            redis_client.close()
            # Shutdown the executor
            executor.shutdown(wait=True)


    async def start_logging_all_sensors(self):
        self.logging_active = True
        tasks = [self.load_cell_logging(name) for name in self.load_cells]
        await asyncio.gather(*tasks)

        return {"message": "Logging started"}


    async def stop_load_cell_logging(self, load_cell_name: str):
        # Ensure logging is marked as inactive
        self.logging_active = False

        # Initialize Redis connection
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Create a ThreadPoolExecutor for running synchronous Redis operations
        executor = ThreadPoolExecutor()

        try:
            # Fetch data from Redis asynchronously using executor
            data = await asyncio.get_event_loop().run_in_executor(executor, lambda: redis_client.lrange(f"load_data:{load_cell_name}", 0, -1))

            # Define directory for saving data
            directory = os.path.join(os.getcwd(), f'logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}/load_cell')
            # Define filename for saving data
            os.makedirs(directory, exist_ok=True)
            filename = os.path.join(directory, f'{load_cell_name}.csv')

            # Write data to file asynchronously
            async with aiofiles.open(filename, 'w') as file:
                await file.write("Force,Time\n")
                data.sort(key = lambda x: x.split(",")[-1])
                for entry in data:
                    await file.write(f"{entry}\n")
        finally:
            # Close Redis connection and shutdown executor
            redis_client.close()
            executor.shutdown(wait=True)

    async def end_logging_all_sensors(self):
        # Ensure logging is marked as inactive
        self.logging_active = False

        # Create tasks for each sensor to stop logging and save data
        tasks = [self.stop_load_cell_logging(name) for name in self.load_cells]
        await asyncio.gather(*tasks) 
        pass