from dataclasses import dataclass, field
import logging
from backend.control.labjack import LabJack
import asyncio
from backend.actuators.abstractActuator import AbstractActuator

logger = logging.getLogger(__name__)

@dataclass
class Relay(AbstractActuator):
    """
    Represents a relay actuator controlled via digital pins.
    
    Attributes:
        name (str): Name of the relay.
        pin (int): Pin number associated with the relay.
    """
    name: str
    pin: int

    def __post_init__(self):
        super().__init__(self.name)  # Initialize AbstractActuator

    async def setup(self):
        """
        Sets up the relay. No setup required for relay actuators.
        """
        pass # No setup required for relay

    async def move_to_safe_position(self):
        """
        Resets the relay to its safe (off) position.
        """
        await self.reset()
        self.logger.info(f"Relay {self.name} moved to safe position")
    
    async def fire(self):
        """
        Activates the relay by setting the pin high.
        """
        await self.labjack.write(self.pin, 1) # Assuming relay is active high
        await self.trigger_actuated_event(1)
        self.logger.info(f"Relay {self.name} moved to on position")

    async def reset(self):
        """
        Deactivates the relay by setting the pin low.
        """
        await self.labjack.write(self.pin, 0) # Assuming relay is active high
        await self.trigger_actuated_event(0)
        self.logger.info(f"Relay {self.name} reset to off position")

    async def pulse(self, pulse_time: int):
        """
        Pulses the relay for a specified duration.
        
        Args:
            pulse_time (int): Duration in seconds to keep the relay active.
        """
        await self.fire()
        await asyncio.sleep(pulse_time)
        await self.reset()
