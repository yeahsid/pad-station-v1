from abc import ABC, abstractmethod
import logging
import asyncio
from backend.control.labjack import LabJack

class AbstractActuator(ABC):

    logger = logging.getLogger(__name__)

    def __init__(self, labjack: LabJack, name: str, actuator_type: str):
        self.labjack = labjack
        self.name = name
        self.actuated_event = asyncio.Event()
        self.position = None
        self.event_handlers = []

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
