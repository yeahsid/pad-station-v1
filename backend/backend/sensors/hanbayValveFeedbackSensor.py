from backend.sensors.abstractSensors import AbstractDigitalSensor
from dataclasses import dataclass
from backend.util.constants import HanbayValveState, HanbayValveEncodings

@dataclass
class HanbayValveFeedbackSensor(AbstractDigitalSensor):
    valve_output_pins = tuple[str, str] # (out0, out1)

    async def setup(self):
        pass # No setup required for hanbay valve feedback sensor

    async def read(self) -> HanbayValveState:
        out0 = await self.labjack.read(self.valve_output_pins[0])
        out1 = await self.labjack.read(self.valve_output_pins[1])
        return HanbayValveEncodings.output[(out0, out1)]