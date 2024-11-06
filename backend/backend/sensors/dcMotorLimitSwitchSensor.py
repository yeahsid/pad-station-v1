from backend.sensors.abstractSensors import AbstractDigitalSensor
from dataclasses import dataclass
from backend.util.constants import DCMotorState

@dataclass
class DcMotorLimitSwitchSensor(AbstractDigitalSensor):
    """
    Represents a digital sensor for DC motor limit switches.

    Attributes:
        name (str): The name of the sensor.
        limit_switch_open_pin (str): Pin connected to the open limit switch.
        limit_switch_close_pin (str): Pin connected to the close limit switch.
    """
    name: str
    limit_switch_open_pin: str
    limit_switch_close_pin: str

    def __post_init__(self):
        """Initialize the DcMotorLimitSwitchSensor."""
        super().__init__(self.name)

    async def setup(self):
        """Setup method for DcMotorLimitSwitchSensor. No setup required."""
        pass  # No setup required for DC motor limit switch sensor

    async def read(self) -> DCMotorState:
        """
        Read the current state of the DC motor based on limit switch pins.

        Returns:
            DCMotorState: The current state of the DC motor.
        """
        ls_open = await self.labjack.read(self.limit_switch_open_pin)
        ls_close = await self.labjack.read(self.limit_switch_close_pin)
        # Determine the motor state based on pin readings
        if ls_open == 0 and ls_close == 1:  # 0 if pressed, 1 if not pressed
            return DCMotorState.OPEN
        elif ls_open == 1 and ls_close == 0:
            return DCMotorState.CLOSE
        else:
            return DCMotorState.INTERMEDIATE