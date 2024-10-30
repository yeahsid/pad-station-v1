from dataclasses import dataclass
import logging
from backend.actuators.servo import Servo

ACTIVE_VENT_CLOSED = 95000  # RICKY CHANGE THIS
ACTIVE_VENT_OPEN = 111000  # RICKY CHANGE THIS

@dataclass
class ActiveVent(Servo):
    power_relay_pin: str
    open_position: int = ACTIVE_VENT_OPEN
    closed_position: int = ACTIVE_VENT_CLOSED

    logger = logging.getLogger(__name__)

    async def setup(self):
        await super().setup()
        await self.labjack.write(self.power_relay_pin, 1)
        self.logger.info(f"Active Vent {self.name} setup complete")

    async def move_to_open(self):
        await self.actuate_servo(self.open_position)
        self.logger.info(f"Active Vent {self.name} moved to open position")

    async def move_to_close(self):
        await self.actuate_servo(self.closed_position)
        self.logger.info(f"Active Vent {self.name} moved to closed position")