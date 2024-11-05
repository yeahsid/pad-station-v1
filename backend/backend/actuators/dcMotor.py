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
    name: str
    motor_enable_pin: str
    motor_in_pins: tuple[str, str]
    limit_switch_open_pin: str
    limit_switch_close_pin: str
    safe_position: BinaryPosition
    limit_switch_sensor: DcMotorLimitSwitchSensor

    def __post_init__(self):
        super().__init__(self.name)

    logger = logging.getLogger(__name__)

    async def setup(self):
        pass # No setup required for dc motor

    async def move_to_safe_position(self):
        await self.move_motor_to_position(self.safe_position, timeout=50)
        self.logger.info(f"{self.name} motor moved to safe position")

    async def stop_motor(self):
        await self.labjack.write(self.motor_enable_pin, 0)
        self.logger.info(f"{self.name} motor stopped")

    async def spin_motor(self, position: BinaryPosition):
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
        count = 0
        last_state: DCMotorState = await self.limit_switch_sensor.read()

        await self.trigger_actuated_event(last_state.value)

        while True:
            state: DCMotorState = await self.limit_switch_sensor.read()

            if state != last_state:
                await self.trigger_actuated_event(state.value)
                last_state = state

            if state.value == position.value:
                count += 1
            else:
                count = 0

            if count == CONSECUTIVE_READS:
                self.logger.info(f"Limit switch {position.name} reached")
                return True
            
            await asyncio.sleep(0.01)

    async def move_motor_to_position(self, position: BinaryPosition, timeout: int):
        await self.spin_motor(position)

        try:
            await asyncio.wait_for(self.wait_for_limit_switch(position), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"{self.name} motor timed out after {timeout} seconds while moving to {position.name} position")
            pass

        await self.stop_motor()
        self.logger.info(f"{self.name} motor moved to {position.name} position")
