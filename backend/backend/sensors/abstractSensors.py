from abc import ABC, abstractmethod
import logging
from backend.control.labjack import LabJack
import re
from enum import Enum
import asyncio

class AbstractAnalogSensor(ABC):

    logger = logging.getLogger(__name__)

    def __init__(self, name: str, unit: str, streaming_address = None):
        self.name = name
        self.unit = unit
        self.labjack = LabJack()  # Access the singleton instance directly
        self.streaming_address = streaming_address # See https://support.labjack.com/docs/3-1-modbus-map-t-series-datasheet to find the addresses of the pins.
        self.streaming_value = None

        try:
            try:
                # Check for an existing event loop
                loop = asyncio.get_running_loop()
                loop.create_task(self.setup())  # Schedule setup in the running loop
            except RuntimeError:
                # If no loop is running, use asyncio.run()
                asyncio.run(self.setup())
            self.logger.info(f"Sensor {self.name} setup complete")
        except Exception as e:
            self.logger.error(f"Sensor {self.name} setup failed: {e}")
            raise e
        
    @abstractmethod
    async def setup(self):
        pass

    @abstractmethod
    def convert(self, raw_value: float) -> float:
        pass

    @abstractmethod
    async def get_raw_value(self) -> float:
        pass

    async def read(self) -> float:
        if self.streaming_value:
            return self.streaming_value
        
        raw_value = await self.get_raw_value()
        return self.convert(raw_value)

class AbstractDigitalSensor(ABC):

    logger = logging.getLogger(__name__)

    def __init__(self, name: str):
        self.name = name
        self.labjack = LabJack()  # Access the singleton instance directly

        try:
            try:
                # Check for an existing event loop
                loop = asyncio.get_running_loop()
                loop.create_task(self.setup())  # Schedule setup in the running loop
            except RuntimeError:
                # If no loop is running, use asyncio.run()
                asyncio.run(self.setup())
            self.logger.info(f"Sensor {self.name} setup complete")
        except Exception as e:
            self.logger.error(f"Sensor {self.name} setup failed: {e}")
            raise e

    @abstractmethod
    async def setup(self):
        pass

    @abstractmethod
    async def read(self) -> Enum:
        pass

def extract_number_from_ain(ain_string):
    match = re.search(r'\d+', ain_string)
    if match:
        return int(match.group())
    else:
        raise ValueError("No number found in the string")






