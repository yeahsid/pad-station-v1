from backend.sensors.abstractSensors import AbstractDigitalSensor
from dataclasses import dataclass
from backend.util.constants import DCMotorState

@dataclass
class DcMotorLimitSwitchSensor(AbstractDigitalSensor):
    name: str
    limit_switch_open_pin: str
    limit_switch_close_pin: str

    def __post_init__(self):
        super().__init__(self.name)

    async def setup(self):
        pass  # No setup required for DC motor limit switch sensor

    async def read(self) -> DCMotorState:
        ls_open = await self.labjack.read(self.limit_switch_open_pin)
        ls_close = await self.labjack.read(self.limit_switch_close_pin)
        if ls_open == 1 and ls_close == 0:
            return DCMotorState.OPEN
        elif ls_open == 0 and ls_close == 1:
            return DCMotorState.CLOSE
        else:
            return DCMotorState.INTERMEDIATE