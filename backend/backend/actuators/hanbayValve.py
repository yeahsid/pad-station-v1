from dataclasses import dataclass, field
import logging
import asyncio
from backend.actuators.abstractActuator import AbstractActuator
from backend.util.constants import HanbayValveEncodings, BinaryPosition, HanbayValveState
from backend.sensors.hanbayValveFeedbackSensor import HanbayValveFeedbackSensor
from backend.control.labjack import LabJack

logger = logging.getLogger(__name__)

@dataclass
class HanbayValve(AbstractActuator):
    name: str
    actuator_type: str
    input_pins: tuple[str, str]
    output_pins: tuple[str, str]
    is_high_high_open: bool
    safe_position: BinaryPosition
    output_state_sensor: HanbayValveFeedbackSensor
    valve_inputs: dict = field(init=False)

    def __post_init__(self):
        super().__init__(self.name)  # No need to initialize labjack here
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
        
        last_state = await self.output_state_sensor.read()
        await self.trigger_actuated_event(last_state)
        while True:
            await asyncio.sleep(0.2)
            state = await self.output_state_sensor.read()

            if state == HanbayValveState.IN_POSITION:
                await self.trigger_actuated_event(state)
                break

            if state != last_state:
                self.logger.info(f"Valve {self.name} state changed to {state}")
                await self.trigger_actuated_event(state)

        self.logger.info(f"HanbayValve {self.name} actuated to {position}")
