from dataclasses import dataclass
import logging
import asyncio
from backend.actuators.abstractActuator import AbstractActuator
from backend.util.constants import BinaryPosition
from backend.control.labjack import LabJack

logger = logging.getLogger(__name__)

CONSECUTIVE_READS = 2

@dataclass
class DcMotor(AbstractActuator):
    name: str
    motor_enable_pin: str
    motor_in_pins: tuple[str, str]
    limit_switch_open_pin: str | None
    limit_switch_close_pin: str | None
    safe_position: BinaryPosition

    def __post_init__(self):
        super().__init__(self.name)  # No need to initialize labjack here

    logger = logging.getLogger(__name__)

    async def setup(self):
        pass # No setup required for dc motor

    async def move_to_safe_position(self):
        await self.move_motor_to_position(self.safe_position, timeout=50)
        self.logger.info(f"Motor {self.name} moved to safe position")

    async def stop_motor(self):
        await self.labjack.write(self.motor_enable_pin, 0)
        self.logger.info(f"Motor {self.name} stopped")

    async def spin_motor(self, position: BinaryPosition):
        await self.labjack.write(self.motor_enable_pin, 1)
        if position == BinaryPosition.OPEN:
            await self.labjack.write(self.motor_in_pins[0], 1)
            await self.labjack.write(self.motor_in_pins[1], 0)
            self.logger.info(f"Motor {self.name} spinning to open")
        elif position == BinaryPosition.CLOSE:
            await self.labjack.write(self.motor_in_pins[0], 0)
            await self.labjack.write(self.motor_in_pins[1], 1)
            self.logger.info(f"Motor {self.name} spinning to close")
        else:
            raise ValueError(f"Invalid position: {position}. Must be '{BinaryPosition.OPEN}' or '{BinaryPosition.CLOSE}'")

    async def wait_for_limit_switch(self, position: BinaryPosition):
        if position == BinaryPosition.OPEN:
            pin = self.limit_switch_open_pin
        elif position == BinaryPosition.CLOSE:
            pin = self.limit_switch_close_pin
        else:
            raise ValueError(f"Invalid position: {position}. Must be '{BinaryPosition.OPEN}' or '{BinaryPosition.CLOSE}'")

        if not pin:
            raise ValueError("No limit switch pin provided")
        
        count = 0
        while True:
            if await self.labjack.read(pin) == 1:
                count += 1
            else:
                count = 0
            if count == CONSECUTIVE_READS:
                self.logger.info(f"Limit switch {position.value} reached")
                return True
            await asyncio.sleep(0.01)

    async def move_motor_to_position(self, position: BinaryPosition, timeout: int):
        await self.spin_motor(position)
        await self.trigger_actuated_event(-1)
        limit_switch_pin = self.limit_switch_open_pin if position == BinaryPosition.OPEN else self.limit_switch_close_pin
        if limit_switch_pin is None:
            logger.warning(f"Motor {self.name} has no limit switch for {position.value} position. Running for {timeout} seconds")
            await asyncio.sleep(timeout)
        else:
            try:
                await asyncio.wait_for(self.wait_for_limit_switch(position), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Motor {self.name} timed out after {timeout} seconds while moving to {position.value} position")
                pass
        await self.stop_motor()
        await self.trigger_actuated_event(position.value)
        self.logger.info(f"Motor {self.name} moved to {position.value} position")
