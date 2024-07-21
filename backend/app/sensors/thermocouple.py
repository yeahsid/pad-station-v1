from collections import deque
from dataclasses import dataclass
import asyncio
from datetime import datetime, timezone
import logging
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import ThermocoupleSensorError
from app.config import LABJACK_PINS
import aiofiles
import redis
from concurrent.futures import ThreadPoolExecutor


import csv
import os
from pathlib import Path

LOGGING_RATE = 1  # Time between tc log points in seconds
POLLING_RATE = 0.1  # Time between tc readings in seconds

logger = logging.getLogger(__name__)


@dataclass
class Thermocouple:
    thermo_pin: str


class ThermocoupleSensor:
    """
    Represents a thermocouple sensor that measures temperature using LabJackConnection.

    Attributes:
        thermocouples (dict): A dictionary of thermocouples, where the keys are the names of the thermocouples
            and the values are instances of the Thermocouple class.
        labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
    """

    def __init__(self, labjack: LabJackConnection, filter_size: int = 10):
        """
        Initializes a ThermocoupleSensor object.

        Args:
            labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
        """
        self.thermocouples = {
            "engine": Thermocouple(LABJACK_PINS["thermocouple_engine"]),
        }
        self.labjack = labjack

        self.thermocouple_setup = False

        self.logging_active = False

    def _get_thermocouple(self, thermocouple_name: str) -> Thermocouple:
        """
        Retrieves the specified thermocouple.

        Args:
            thermocouple_name (str): The name of the thermocouple.

        Returns:
            Thermocouple: The specified thermocouple.

        Raises:
            ThermocoupleSensorError: If the specified thermocouple is not found.
        """
        try:
            return self.thermocouples[thermocouple_name]
        except KeyError:
            logger.error("Thermocouple not found")
            raise ThermocoupleSensorError("Thermocouple not found")
        

    async def _thermocouple_setup(self, thermocouple_name: str):
        """
        Sets up the LabJack device to read from the specified thermocouple.

        Args:
            thermocouple_name (str): The name of the thermocouple.
        """
        thermocouple = self._get_thermocouple(thermocouple_name)

        # Set up the thermocouple
        await self.labjack.write(f"{thermocouple.thermo_pin}_EF_INDEX", 22)
        await self.labjack.write(f"{thermocouple.thermo_pin}_EF_CONFIG_A", 1)
        await self.labjack.write(f"{thermocouple.thermo_pin}_EF_CONFIG_B", 60052)
        await self.labjack.write(f"{thermocouple.thermo_pin}_EF_CONFIG_D", 1.0)
        await self.labjack.write(f"{thermocouple.thermo_pin}_EF_CONFIG_E", 0.0)

    async def get_thermocouple_temperature(self, thermocouple_name: str) -> float:
        """
        Get the temperature reading from a thermocouple.

        Args:
            thermocouple_name (str): The name of the thermocouple.

        Returns:
            float: The temperature reading in degrees Celsius.
        """
        thermocouple = self._get_thermocouple(thermocouple_name)
        if not self.thermocouple_setup:
            await self._thermocouple_setup(thermocouple_name)
            self.thermocouple_setup = True


        temperature = await self.labjack.read(f"{thermocouple.thermo_pin}_EF_READ_A")

        return temperature

    async def thermocouple_datastream(self, thermocouple_name: str):
        """
        Creates a data stream of temperature readings from the specified thermocouple.

        Args:
            thermocouple_name (str): The name of the thermocouple.

        Yields:
            float: The next temperature reading from the specified thermocouple.
        """

        while True:
            temperature = await self.get_thermocouple_temperature(thermocouple_name)
            yield temperature
            await asyncio.sleep(POLLING_RATE)
    
    async def thermocouple_logging(self, thermocouple_name: str):
        # Initialize Redis connection
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Create a ThreadPoolExecutor
        executor = ThreadPoolExecutor()

        try:
            while self.logging_active:
                temperature_reading = await self.get_thermocouple_temperature(thermocouple_name)
                current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                
                # Create a structured string or a dictionary to represent the data
                data = f"{temperature_reading},{current_time}"
                
                # Use run_in_executor to run the synchronous Redis operation in a separate thread
                await asyncio.get_event_loop().run_in_executor(executor, lambda: redis_client.lpush(f"temperature_data:{thermocouple_name}", data))
                
                await asyncio.sleep(LOGGING_RATE)
        finally:
            # Close Redis connection outside of the loop
            redis_client.close()
            # Shutdown the executor
            executor.shutdown(wait=True)


    async def start_logging_all_sensors(self):
        self.logging_active = True
        tasks = [self.thermocouple_logging(name) for name in self.thermocouples]
        await asyncio.gather(*tasks)

        return {"message": "Logging started"}


    async def stop_thermocouple_logging(self, thermocouple_name: str):
        # Ensure logging is marked as inactive
        self.logging_active = False

        # Initialize Redis connection
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Create a ThreadPoolExecutor for running synchronous Redis operations
        executor = ThreadPoolExecutor()

        try:
            # Fetch data from Redis asynchronously using executor
            data = await asyncio.get_event_loop().run_in_executor(executor, lambda: redis_client.lrange(f"temperature_data:{thermocouple_name}", 0, -1))

            # Define filename for saving data
            filename = os.path.join(os.getcwd(), f'logs/thermocouple/{thermocouple_name}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv')

            # Write data to file asynchronously
            async with aiofiles.open(filename, 'w') as file:
                await file.write("Temperature,Time\n")
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
        tasks = [self.stop_thermocouple_logging(name) for name in self.thermocouples]
        await asyncio.gather(*tasks)