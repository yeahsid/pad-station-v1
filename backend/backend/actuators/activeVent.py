from dataclasses import dataclass, field
import logging
from backend.actuators.servo import Servo
from backend.actuators.relay import Relay
from backend.util.config import ACTIVE_VENT_CLOSED_POSITION, ACTIVE_VENT_OPEN_POSITION

class ActiveVent(Servo):
    def __init__(self, name: str, pwm_pin: str, default_position: int, 
                 safe_position: int, power_relay: Relay):
        
        super().__init__(name, pwm_pin, default_position, safe_position)

        self.power_relay = power_relay
        self.open_position = ACTIVE_VENT_OPEN_POSITION
        self.closed_position = ACTIVE_VENT_CLOSED_POSITION

    logger = logging.getLogger(__name__)

    async def setup(self):
        await super().setup()
        await self.power_relay.fire()
        self.logger.info(f"Active Vent {self.name} setup complete")

    async def move_to_open(self):
        await self.actuate_servo(self.open_position)
        self.logger.info(f"Active Vent {self.name} moved to open position")

    async def move_to_close(self):
        await self.actuate_servo(self.closed_position)
        self.logger.info(f"Active Vent {self.name} moved to closed position")