from dataclasses import dataclass, field
import logging
from backend.control.labjack import LabJack
import asyncio
from backend.actuators.abstractActuator import AbstractActuator

logger = logging.getLogger(__name__)

@dataclass
class Relay(AbstractActuator):
    name: str
    pin: int

    def __post_init__(self):
        super().__init__(self.name)  # No need to initialize labjack here

    async def setup(self):
        pass # No setup required for relay

    async def move_to_safe_position(self):
        await self.reset()
        self.logger.info(f"Relay {self.name} moved to safe position")
    
    async def fire(self):
        await self.labjack.write(self.pin, 1) # Assuming relay is active high
        await self.trigger_actuated_event(1)
        self.logger.info(f"Relay {self.name} moved to on position")

    async def reset(self):
        await self.labjack.write(self.pin, 0) # Assuming relay is active high
        await self.trigger_actuated_event(0)
        self.logger.info(f"Relay {self.name} reset to off position")

    async def pulse(self, pulse_time: int):
        await self.fire()
        await asyncio.sleep(pulse_time)
        await self.reset()
