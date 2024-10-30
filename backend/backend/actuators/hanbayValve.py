from dataclasses import dataclass
import logging
from backend.actuators.actuator import Actuator
from backend.util.constants import HanbayValveEncodings, BinaryPosition

logger = logging.getLogger(__name__)

@dataclass
class HanbayValve(Actuator):
    input_pins: tuple[str, str] # (in0, in1)
    output_pins: tuple[str, str] # (out0, out1)
    is_high_high_open: bool
    safe_position: BinaryPosition

    def __post_init__(self):
        if self.is_high_high_open:
            self.valve_inputs = HanbayValveEncodings.input_high_high_open
        else:
            self.valve_inputs = HanbayValveEncodings.input_high_low_open

    logger = logging.getLogger(__name__)

    async def setup(self):
        pass

    async def move_to_safe_position(self):
        await self.actuate_valve(self.safe_position)
        self.logger.info(f"Valve {self.name} moved to safe position")

    async def actuate_valve(self, position: BinaryPosition):
        await self.labjack.write(self.input_pins[0], self.valve_inputs[position][0])
        await self.labjack.write(self.input_pins[1], self.valve_inputs[position][1])
        self.logger.info(f"HanbayValve {self.name} actuated to {position}")
