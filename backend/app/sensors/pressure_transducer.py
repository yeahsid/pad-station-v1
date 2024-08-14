from collections import deque
from dataclasses import dataclass
import asyncio
from datetime import datetime, timezone
import logging
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import PressureSensorError
from app.config import LABJACK_PINS
import redis
import aiofiles
from concurrent.futures import ThreadPoolExecutor


import csv
import os
from typing import Tuple


LOGGING_RATE = 0.001  # Time between pt log points in seconds
POLLING_RATE = 0.25  # Time between pt readings in seconds

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
            "fill": PressureTransducer(LABJACK_PINS["pressure_transducer_fill"], 200),
            "tank_top": PressureTransducer(LABJACK_PINS["pressure_transducer_tank"], 200),
            "chamber": PressureTransducer(LABJACK_PINS["pressure_transducer_chamber"], 200),
        }
        self.pressure_transducers_to_log = list(self.pressure_transducers.keys())[2:]
        self.labjack = labjack
        self.logging_active = False  # Used to disable logging at a chosen time

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

    async def get_pressure_transducer_feedback(self, pressure_transducer_name: str) -> Tuple[float, float]:
        pressure_transducer = self._get_pressure_transducer(pressure_transducer_name)
        voltage = await self.labjack.read(pressure_transducer.pressure_signal)
        # Calculate pressure from voltage
        # pressure = (voltage - 0.5) / 4 * pressure_transducer.max_pressure
        pressure = (voltage * 54.87) - 25.82
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
            pressure_reading, voltage = await self.get_pressure_transducer_feedback(pressure_transducer_name)
            yield pressure_reading
            await asyncio.sleep(POLLING_RATE)

    async def pressure_transducer_logging(self, pressure_transducer_name: str):
        # Initialize Redis connection
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Create a ThreadPoolExecutor
        executor = ThreadPoolExecutor()

        try:
            while self.logging_active:
                pressure_reading, voltage = await self.get_pressure_transducer_feedback(pressure_transducer_name)
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                
                # Create a structured string or a dictionary to represent the data
                data = f"{pressure_reading},{voltage},{current_time}"
                
                # Use run_in_executor to run the synchronous Redis operation in a separate thread
                await asyncio.get_event_loop().run_in_executor(executor, lambda: redis_client.lpush(f"pressure_data:{pressure_transducer_name}", data))
                
                await asyncio.sleep(LOGGING_RATE)
        finally:
            # Close Redis connection outside of the loop
            redis_client.close()
            # Shutdown the executor
            executor.shutdown(wait=True)


    async def start_logging_all_sensors(self):
        self.logging_active = True
        tasks = [self.pressure_transducer_logging(name) for name in self.pressure_transducers]
        await asyncio.gather(*tasks)

        return {"message": "Logging started"}


    async def stop_pressure_transducer_logging(self, pressure_transducer_name: str):
        # Ensure logging is marked as inactive
        self.logging_active = False

        # Initialize Redis connection
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


        # Create a ThreadPoolExecutor for running synchronous Redis operations
        executor = ThreadPoolExecutor()
        redis_client.delete(f"pressure_data:{pressure_transducer_name}")

        try:
            # Fetch data from Redis asynchronously using executor
            data = await asyncio.get_event_loop().run_in_executor(executor, lambda: redis_client.lrange(f"pressure_data:{pressure_transducer_name}", 0, -1))

            # Define directory for saving data
            directory = os.path.join(os.getcwd(), f'logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}/pressure')
            # Define filename for saving data
            os.makedirs(directory, exist_ok=True)
            filename = os.path.join(directory, f'{pressure_transducer_name}.csv')

            # Write data to file asynchronously
            async with aiofiles.open(filename, 'w') as file:
                await file.write("Pressure Reading,Voltage,Time\n")
                data.sort(key = lambda x: x.split(",")[-1])
                for entry in data:
                    await file.write(f"{entry}\n")
        finally:
            # Close Redis connection and shutdown executor

            logger.info(f"Data saved to {filename}")
            redis_client.close()
            executor.shutdown(wait=True)

    async def end_logging_all_sensors(self):
        # Ensure logging is marked as inactive
        self.logging_active = False

        # Create tasks for each sensor to stop logging and save data
        tasks = [self.stop_pressure_transducer_logging(name) for name in self.pressure_transducers_to_log]
        await asyncio.gather(*tasks)

        