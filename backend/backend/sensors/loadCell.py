from dataclasses import dataclass
import logging
from backend.sensors.abstractLabjackSensors import AbstractAnalogSensorLJ, extract_number_from_ain
from backend.util.config import LOAD_CELL_CALIBRATION
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class LoadCell(AbstractAnalogSensorLJ):
    """
    Represents a Load Cell sensor for measuring force.

    Attributes:
        name (str): The name of the sensor.
        signal_pos (str): The positive signal pin connected to the LabJack.
        signal_neg (str): The negative signal pin connected to the LabJack.
        streaming_enabled (bool): Flag to enable streaming of sensor data.
        calibration (tuple): Calibration offset and scale.
        tare_reading (float): Tare value to zero the sensor.
    """
    name: str
    signal_pos: str
    signal_neg: str
    streaming_enabled: bool
    calibration: tuple[float, float] = LOAD_CELL_CALIBRATION
    tare_reading: float = 0.0

    def __post_init__(self):
        """Initialize the LoadCell sensor with Modbus address."""
        modbus_address = int(extract_number_from_ain(self.signal_pos)) * 2  # Convert signal_pos to Modbus address
        super().__init__(self.name, "N", self.streaming_enabled, modbus_address)

    async def setup(self):
        """Configure the LabJack settings for the LoadCell."""
        await self.labjack.write(f"{self.signal_pos}_RANGE", 0.1)
        await self.labjack.write(f"{self.signal_pos}_RESOLUTION_INDEX", 0)
        await self.labjack.write(f"{self.signal_pos}_NEGATIVE_CH", extract_number_from_ain(self.signal_neg))
        await self.labjack.write(f"{self.signal_pos}_SETTLING_US", 0)

    def convert_single(self, raw_value: float) -> float:
        """
        Convert a single raw voltage value to force in Newtons.

        Args:
            raw_value (float): The raw voltage value from the sensor.

        Returns:
            float: The converted force value rounded to three decimals.
        """
        # Apply calibration offset and scale
        force = raw_value * self.calibration[1] + self.calibration[0]
        # Subtract tare reading to zero the sensor
        force -= self.tare_reading
        return np.round(force, 3)
    
    def convert_array(self, raw_value_array: np.ndarray) -> np.ndarray:
        """
        Convert an array of raw voltage values to forces in Newtons.

        Args:
            raw_value_array (np.ndarray): Array of raw voltage values.

        Returns:
            np.ndarray: Array of converted force values rounded to three decimals.
        """
        # Apply calibration offset and scale
        force_array = raw_value_array * self.calibration[1] + self.calibration[0]
        # Subtract tare reading to zero the sensor
        force_array -= self.tare_reading
        return force_array.round(3)

    async def get_raw_value(self) -> float:
        """
        Retrieve the raw voltage value from the LabJack.

        Returns:
            float: The raw voltage reading.
        """
        voltage = await self.labjack.read(self.signal_pos)
        return voltage

    async def tare(self):
        """
        Perform tare operation to zero the sensor by updating tare_reading.
        """
        # Read the current value and update tare_reading
        self.tare_reading = await self.read() + self.tare_reading
