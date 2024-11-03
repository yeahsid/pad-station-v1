from abc import ABC, abstractmethod
import logging
import asyncio
from backend.control.labjack import LabJack

class AbstractActuator(ABC):
    logger = logging.getLogger(__name__)

    def __init__(self, name: str):
        self.name = name
        self.labjack = LabJack()  # Access the singleton instance directly
        self.actuated_event = asyncio.Event()
        self.position = None
        self.event_handlers = []

        try:
            asyncio.run(self.setup())
            self.logger.info(f"{self.name} setup complete")
        except Exception as e:
            self.logger.error(f"{self.name} setup failed: {e}")

    @abstractmethod
    async def setup(self):
        raise NotImplementedError()

    @abstractmethod
    async def move_to_safe_position(self):
        raise NotImplementedError()
    
    def register_event_handler(self, handler):
        self.event_handlers.append(handler)

    async def trigger_actuated_event(self, position):
        self.position = position 
        self.actuated_event.set()
        for handler in self.event_handlers:
            await handler(self, position)

    async def event_handler(self):
        await self.actuated_event.wait()  # Wait for the event to be set
        # self.logger.info(f"Event has been set! Arguments: {self.event_args}")
