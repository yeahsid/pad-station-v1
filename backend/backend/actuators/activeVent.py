from dataclasses import dataclass, field
import logging
from backend.actuators.servo import Servo
from backend.config import ACTIVE_VENT_CLOSED_POSITION, ACTIVE_VENT_OPEN_POSITION

@dataclass
class ActiveVent(Servo):
    name: str
    actuator_type: str
    pwm_pin: str
    default_position: int
    safe_position: int
    power_relay_pin: str
    open_position: int = field(default=ACTIVE_VENT_OPEN_POSITION, init=False)
    closed_position: int = field(default=ACTIVE_VENT_CLOSED_POSITION, init=False)

    def __post_init__(self):
        super().__init__(self.name, self.pwm_pin, self.default_position, self.safe_position)  # No need to initialize labjack here

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