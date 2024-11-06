from backend.sensors.abstractSensors import AbstractDigitalSensor
from dataclasses import dataclass
from backend.util.constants import HanbayValveState, HanbayValveEncodings

@dataclass
class HanbayValveFeedbackSensor(AbstractDigitalSensor):
    """
    Represents a digital feedback sensor for Hanbay valves.

    Attributes:
        name (str): The name of the sensor.
        valve_output_pins (tuple[str, str]): Tuple containing the two output pins for the valve.
    """
    name: str
    valve_output_pins: tuple[str, str]  # (out0, out1)
    
    def __post_init__(self):
        """Initialize the HanbayValveFeedbackSensor."""
        super().__init__(self.name)

    async def setup(self):
        """Setup method for HanbayValveFeedbackSensor. No setup required."""
        pass  # No setup required for hanbay valve feedback sensor

    async def read(self) -> HanbayValveState:
        """
        Read the current state of the Hanbay valve based on output pins.

        Returns:
            HanbayValveState: The current state of the valve.
        """
        out0 = await self.labjack.read(self.valve_output_pins[0])
        out1 = await self.labjack.read(self.valve_output_pins[1])
        # Determine the valve state based on pin readings
        return HanbayValveEncodings.output[(out0, out1)]