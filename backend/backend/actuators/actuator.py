from abc import ABC, abstractmethod
import logging
import asyncio
from backend.labjackHardware.labjack import LabJack

class Actuator(ABC):

    logger = logging.getLogger(__name__)

    def __init__(self, labjack: LabJack, name: str, actuator_type: str):
        self.labjack = labjack
        self.name = name

        try:
            asyncio.run(self.setup())
            self.logger.info(f"{actuator_type} {self.name} setup complete")
        except Exception as e:
            self.logger.error(f"{actuator_type} {self.name} setup failed: {e}")

    @abstractmethod
    async def setup(self):
        raise NotImplementedError()

    @abstractmethod
    async def move_to_safe_position(self):
        raise NotImplementedError()