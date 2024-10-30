from dataclasses import dataclass
import logging
from backend.labjackHardware.labjack import LabJack
import asyncio
from backend.actuators.actuator import Actuator

logger = logging.getLogger(__name__)

@dataclass
class Relay(Actuator):
    pin: int

    logger = logging.getLogger(__name__)

    async def setup(self):
        pass # No setup required for relay

    async def move_to_safe_position(self):
        await self.labjack.write(self.pin, 0) # Assuming relay is active high
        self.logger.info(f"Relay {self.name} moved to safe position")
    
    async def fire(self):
        await self.labjack.write(self.pin, 1) # Assuming relay is active high
        self.logger.info(f"Relay {self.name} moved to on position")

    async def reset(self):
        await self.labjack.write(self.pin, 0) # Assuming relay is active high
        self.logger.info(f"Relay {self.name} reset to off position")

    async def pulse(self, pulse_time: int):
        await self.fire()
        await asyncio.sleep(pulse_time)
        await self.reset()
        
