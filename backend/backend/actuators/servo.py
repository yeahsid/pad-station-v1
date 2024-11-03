from dataclasses import dataclass
import logging
from backend.actuators.abstractActuator import AbstractActuator

@dataclass
class Servo(AbstractActuator):
    pwm_pin: str
    default_position: int
    safe_position: int

    logger = logging.getLogger(__name__)

    async def setup(self):
        # Configure PWM Functionality
        # Should be 80 Hz signal? Ask Ben McDonald so he can tell you what to do
        # Disable clock source
        await self.labjack.write("DIO_EF_CLOCK0_ENABLE", 0)
        # Configure Clock0's divisor and roll value
        await self.labjack.write("DIO_EF_CLOCK0_DIVISOR", 1)
        await self.labjack.write("DIO_EF_CLOCK0_ROLL_VALUE", 1000000)
        # Enable Clock0
        await self.labjack.write("DIO_EF_CLOCK0_ENABLE", 1)

        # Configure EF (Extended Features) Channel Registers:
        # Disable the EF system for initial configuration
        await self.labjack.write(f"{self.pwm_pin}_EF_ENABLE", 0)
        # Configure EF system for PWM output
        await self.labjack.write(f"{self.pwm_pin}_EF_INDEX", 0)
        # Configure what clock source to use: Clock0
        await self.labjack.write(f"{self.pwm_pin}_EF_OPTIONS", 0)
        # Set startup position
        await self.labjack.write(f"{self.pwm_pin}_EF_CONFIG_A", self.default_position)
        # Enable the EF system after completing configuration
        await self.labjack.write(f"{self.pwm_pin}_EF_ENABLE", 1)

        self.logger.info(f"Servo {self.name} setup complete")

    async def move_to_safe_position(self):
        await self.actuate_servo(self.safe_position)
        self.logger.info(f"Servo {self.name} moved to safe position")

    async def actuate_servo(self, position: int):
        await self.labjack.write(f"{self.pwm_pin}_EF_CONFIG_A", position)
        self.trigger_actuated_event(position)
        self.logger.info(f"Servo {self.name} actuated to position {position}")