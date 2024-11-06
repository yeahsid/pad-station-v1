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
    """
    Represents a Hanbay valve actuator controlled via digital pins.
    
    Attributes:
        name (str): Name of the valve.
        input_pins (tuple[str, str]): Input pins for controlling the valve.
        output_pins (tuple[str, str]): Output pins for valve feedback.
        is_high_high_open (bool): Determines the encoding based on valve type.
        safe_position (BinaryPosition): Safe position of the valve.
        output_state_sensor (HanbayValveFeedbackSensor): Sensor for valve state feedback.
        valve_inputs (dict): Encoding mappings for input signals.
    """
    name: str
    input_pins: tuple[str, str]
    output_pins: tuple[str, str]
    is_high_high_open: bool
    safe_position: BinaryPosition
    output_state_sensor: HanbayValveFeedbackSensor
    valve_inputs: dict = field(init=False)

    def __post_init__(self):
        super().__init__(self.name)    # Initialize AbstractActuator
        # Select encoding based on valve type
        if self.is_high_high_open:
            self.valve_inputs = HanbayValveEncodings.input_high_high_open
        else:
            self.valve_inputs = HanbayValveEncodings.input_high_low_open

    logger = logging.getLogger(__name__)

    async def setup(self):
        """
        Sets up the Hanbay valve. No additional setup required.
        """
        pass

    async def move_to_safe_position(self):
        """
        Moves the valve to its predefined safe position.
        """
        await self.actuate_valve(self.safe_position)
        self.logger.info(f"{self.name} moved to safe position")

    async def actuate_valve(self, position: BinaryPosition):
        """
        Actuates the valve to a specified binary position.
        
        Args:
            position (BinaryPosition): Desired position (OPEN or CLOSE).
        """
        # Write input signals based on encoding
        await self.labjack.write(self.input_pins[0], self.valve_inputs[position][0])
        await self.labjack.write(self.input_pins[1], self.valve_inputs[position][1])
        
        # Read the last known state from the sensor
        last_state = await self.output_state_sensor.read()
        await self.trigger_actuated_event(last_state)
        while True:
            await asyncio.sleep(0.2) # Polling interval
            state = await self.output_state_sensor.read()

            if state != last_state:
                self.logger.info(f"{self.name} state changed to {state}")
                await self.trigger_actuated_event(state)
                last_state = state

            if state == HanbayValveState.IN_POSITION:
                await self.trigger_actuated_event(state)
                break           

        self.logger.info(f"{self.name} actuated to {position}")
