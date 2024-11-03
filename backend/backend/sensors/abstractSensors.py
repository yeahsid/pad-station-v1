from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import asyncio
from backend.control.labjack import LabJack
from backend.config import DIGITAL_SENSOR_UPDATE_RATE

class AbstractAnalogSensor(ABC):

    logger = logging.getLogger(__name__)

    def __init__(self, name: str, unit: str):
        self.name = name
        self.unit = unit
        self.labjack = LabJack()  # Access the singleton instance directly
        self.streaming_address = None

        try:
            self.setup()
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
            self.setup()
            self.logger.info(f"Sensor {self.name} setup complete")
        except Exception as e:
            self.logger.error(f"Sensor {self.name} setup failed: {e}")
            raise e

    @abstractmethod
    async def setup(self):
        pass

    @abstractmethod
    async def read(self):
        pass






