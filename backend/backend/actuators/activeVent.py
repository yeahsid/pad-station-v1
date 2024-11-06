from dataclasses import dataclass, field
import logging
from backend.actuators.servo import Servo
from backend.actuators.relay import Relay
from backend.util.config import ACTIVE_VENT_CLOSED_POSITION, ACTIVE_VENT_OPEN_POSITION

class ActiveVent(Servo):
    """
    Represents an active vent controlled by a servo and powered via a relay.
    
    Attributes:
        name (str): Name of the active vent.
        pwm_pin (str): PWM pin identifier for servo control.
        default_position (int): Default PWM position value.
        safe_position (int): PWM position value representing a safe state.
        power_relay (Relay): Relay controlling power to the servo.
        open_position (int): PWM position value for the open state.
        closed_position (int): PWM position value for the closed state.
    """

    def __init__(self, name: str, pwm_pin: str, default_position: int, 
                 safe_position: int, power_relay: Relay):
        """
        Initializes the ActiveVent with necessary pins and relay.
        
        Args:
            name (str): Name of the active vent.
            pwm_pin (str): PWM pin identifier for servo control.
            default_position (int): Default PWM position value.
            safe_position (int): PWM position value representing a safe state.
            power_relay (Relay): Relay controlling power to the servo.
        """
        self.power_relay = power_relay
        self.open_position = ACTIVE_VENT_OPEN_POSITION
        self.closed_position = ACTIVE_VENT_CLOSED_POSITION
        
        super().__init__(name, pwm_pin, default_position, safe_position)

    logger = logging.getLogger(__name__)

    async def setup(self):
        """
        Sets up the active vent by configuring the servo and activating the relay.
        """
        await super().setup()
        await self.power_relay.fire()
        self.logger.info(f"Active Vent {self.name} setup complete")

    async def move_to_open(self):
        """
        Moves the active vent to the open position.
        """
        await self.actuate_servo(self.open_position)
        self.logger.info(f"Active Vent {self.name} moved to open position")

    async def move_to_close(self):
        """
        Moves the active vent to the closed position.
        """
        await self.actuate_servo(self.closed_position)
        self.logger.info(f"Active Vent {self.name} moved to closed position")