from dataclasses import dataclass
import logging
from backend.control.labjack import LabJack
from backend.actuators.abstractActuator import AbstractActuator

@dataclass
class Servo(AbstractActuator):
    """
    Represents a servo actuator controlled via PWM signals.
    
    Attributes:
        name (str): Name of the servo.
        pwm_pin (str): PWM pin identifier for servo control.
        default_position (int): Default PWM position value.
        safe_position (int): PWM position value representing a safe state.
    """
    name: str
    pwm_pin: str
    default_position: int
    safe_position: int

    def __post_init__(self):
        super().__init__(self.name)  # Initialize AbstractActuator

    logger = logging.getLogger(__name__)

    async def setup(self):
        """
        Configures the PWM settings for the servo using the LabJack device.
        """
        # Configure PWM Functionality
        # Should be 80 Hz signal? Ask Ben McDonald so he can tell you what to do
        # 80 MHz / 1 / 1000000 = 80 Hz (within the 50-330Hz range of the servo)
        await self.labjack.write("DIO_EF_CLOCK0_ENABLE", 0) # Disable clock source
        await self.labjack.write("DIO_EF_CLOCK0_DIVISOR", 1) # Don't divide the clock
        await self.labjack.write("DIO_EF_CLOCK0_ROLL_VALUE", 1000000) # 1 million ticks before rollover
        await self.labjack.write("DIO_EF_CLOCK0_ENABLE", 1) # Enable clock source

        # Configure EF (Extended Features) Channel Registers:
        await self.labjack.write(f"{self.pwm_pin}_EF_ENABLE", 0) # Disable EF system for config
        await self.labjack.write(f"{self.pwm_pin}_EF_INDEX", 0) # Set EF index
        await self.labjack.write(f"{self.pwm_pin}_EF_OPTIONS", 0) # Use Clock0 as source
        await self.labjack.write(f"{self.pwm_pin}_EF_CONFIG_A", self.default_position) # Set startup position
        await self.labjack.write(f"{self.pwm_pin}_EF_ENABLE", 1) # Enable EF system after config

        self.logger.info(f"{self.name} servo setup complete")

    async def move_to_safe_position(self):
        """
        Moves the servo to its predefined safe position.
        """
        await self.actuate_servo(self.safe_position)
        self.logger.info(f"{self.name} servo moved to safe position")

    async def actuate_servo(self, position: int):
        """
        Actuates the servo to a specified position.
        
        Args:
            position (int): The PWM position value to move the servo to.
        """
        await self.labjack.write(f"{self.pwm_pin}_EF_CONFIG_A", position)
        self.trigger_actuated_event(position)
        self.logger.info(f"{self.name} servo actuated to position {position}")