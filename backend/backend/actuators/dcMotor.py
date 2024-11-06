from dataclasses import dataclass
import logging
import asyncio
from backend.actuators.abstractActuator import AbstractActuator
from backend.util.constants import BinaryPosition, DCMotorState
from backend.control.labjack import LabJack
from backend.sensors.dcMotorLimitSwitchSensor import DcMotorLimitSwitchSensor

logger = logging.getLogger(__name__)

CONSECUTIVE_READS = 2

@dataclass
class DcMotor(AbstractActuator):
    """
    Represents a DC motor actuator with limit switch feedback.
    
    Attributes:
        name (str): Name of the motor.
        motor_enable_pin (str): Pin to enable the motor.
        motor_in_pins (tuple[str, str]): Pins to control motor direction.
        limit_switch_open_pin (str): Pin for the open limit switch.
        limit_switch_close_pin (str): Pin for the close limit switch.
        safe_position (BinaryPosition): Safe position of the motor.
        limit_switch_sensor (DcMotorLimitSwitchSensor): Sensor for limit switch feedback.
    """
    name: str
    motor_enable_pin: str
    motor_in_pins: tuple[str, str]
    limit_switch_open_pin: str
    limit_switch_close_pin: str
    safe_position: BinaryPosition
    limit_switch_sensor: DcMotorLimitSwitchSensor

    def __post_init__(self):
        super().__init__(self.name)  # Initialize AbstractActuator

    logger = logging.getLogger(__name__)

    async def setup(self):
        """
        Sets up the DC motor. No additional setup required.
        """
        pass # No setup required for dc motor

    async def move_to_safe_position(self):
        """
        Moves the motor to its predefined safe position within a timeout.
        """
        await self.move_motor_to_position(self.safe_position, timeout=50)
        self.logger.info(f"{self.name} motor moved to safe position")

    async def stop_motor(self):
        """
        Stops the motor by disabling it.
        """
        await self.labjack.write(self.motor_enable_pin, 0)
        self.logger.info(f"{self.name} motor stopped")

    async def spin_motor(self, position: BinaryPosition):
        """
        Spins the motor to the specified binary position.
        
        Args:
            position (BinaryPosition): Desired position (OPEN or CLOSE).
        """
        await self.labjack.write(self.motor_enable_pin, 1)
        if position == BinaryPosition.OPEN:
            await self.labjack.write(self.motor_in_pins[0], 1)
            await self.labjack.write(self.motor_in_pins[1], 0)
            self.logger.info(f"{self.name} motor spinning to open")
        elif position == BinaryPosition.CLOSE:
            await self.labjack.write(self.motor_in_pins[0], 0)
            await self.labjack.write(self.motor_in_pins[1], 1)
            self.logger.info(f"{self.name} motor spinning to close")
        else:
            raise ValueError(f"Invalid position: {position}. Must be '{BinaryPosition.OPEN}' or '{BinaryPosition.CLOSE}'")

    async def wait_for_limit_switch(self, position: BinaryPosition):
        """
        Waits until the motor reaches the specified limit switch position.
        
        Args:
            position (BinaryPosition): The limit switch position to wait for.
        
        Returns:
            bool: True if the position is reached within the required reads.
        """
        count = 0
        # Read the initial state of the limit switch
        last_state: DCMotorState = await self.limit_switch_sensor.read()

        # Trigger an event based on the initial state
        await self.trigger_actuated_event(last_state.value)

        while True:
            # Continuously read the current state of the limit switch
            state: DCMotorState = await self.limit_switch_sensor.read()

            if state != last_state:
                # If the state has changed, trigger an event and update the last state
                await self.trigger_actuated_event(state.value)
                last_state = state

            if state.value == position.value:
                count += 1  # Increment count if desired position is detected
            else:
                count = 0  # Reset count if position is not maintained

            if count == CONSECUTIVE_READS:
                # Confirm the position has been consistently detected
                self.logger.info(f"Limit switch {position.name} reached")
                return True
            
            await asyncio.sleep(0.01)  # Short delay to prevent tight loop

    async def move_motor_to_position(self, position: BinaryPosition, timeout: int):
        """
        Moves the motor to a specified position and waits for confirmation via limit switch.
        
        Args:
            position (BinaryPosition): Desired motor position (OPEN or CLOSE).
            timeout (int): Maximum time to wait for the position in seconds.
        """
        await self.spin_motor(position)  # Initiate motor movement

        try:
            # Await confirmation that motor has reached the desired position within the timeout
            await asyncio.wait_for(self.wait_for_limit_switch(position), timeout=timeout)
        except asyncio.TimeoutError:
            # Handle the scenario where the motor does not reach the position in time
            logger.warning(f"{self.name} motor timed out after {timeout} seconds while moving to {position.name} position")
            pass

        await self.stop_motor()  # Stop the motor after movement
        self.logger.info(f"{self.name} motor moved to {position.name} position")
