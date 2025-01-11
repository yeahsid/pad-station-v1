import logging
from backend.sensors.abstractLabjackSensors import AbstractAnalogSensorLJ, extract_number_from_ain
from backend.util.config import PRESSURE_TRANSDUCER_CALIBRATION, PRESSURE_TRANSDUCER_READ_VS, LabJackPeripherals
import numpy as np
import time

class PressureTransducer(AbstractAnalogSensorLJ):
    """
    Represents a Pressure Transducer sensor for measuring pressure.

    Attributes:
        name (str): The name of the sensor.
        pin (str): The LabJack pin connected to the sensor.
        streaming_enabled (bool): Flag to enable streaming of sensor data.
        calibration (tuple): Calibration offset and scale.
        tare_reading (float): Tare value to zero the sensor.
    """
    # Static class variables for shared state
    Vs_voltage: float = 4.7
    Vs_checked_time = time.time()
    Vs_pin: str = LabJackPeripherals.PRESSURE_TRANSDUCER_Vs_PIN.value if PRESSURE_TRANSDUCER_READ_VS else None

    def __init__(self, name: str, pin: str, streaming_enabled: bool):
        """Initialize the PressureTransducer sensor with Modbus address."""
        self.name = name
        self.pin = pin
        self.streaming_enabled = streaming_enabled

        modbus_address = extract_number_from_ain(self.pin) * 2  # Convert AIN to Modbus address
        super().__init__(self.name, "Bar", self.streaming_enabled, modbus_address)

        self.logger = logging.getLogger(__name__)

    async def setup(self):
        """Setup method for PressureTransducer. No setup required."""
        pass  # No setup required for pressure transducer

    def convert_single(self, raw_value: float) -> float:
        """
        Convert a single raw voltage value to pressure in Bar.

        Args:
            raw_value (float): The raw voltage value from the sensor.

        Returns:
            float: The converted pressure value rounded to two decimals.
        """
        # Convert the raw voltage to actual voltage considering Vs_voltage
        raw_value = (raw_value / self.__class__.Vs_voltage) * 4.7
        # Apply calibration offset and scale
        pressure = (raw_value * PRESSURE_TRANSDUCER_CALIBRATION[1]) + PRESSURE_TRANSDUCER_CALIBRATION[0]
        return np.round(pressure, 2)
    
    def convert_array(self, raw_value_array: np.ndarray) -> np.ndarray:
        """
        Convert an array of raw voltage values to pressures in Bar.

        Args:
            raw_value_array (np.ndarray): Array of raw voltage values.

        Returns:
            np.ndarray: Array of converted pressure values rounded to two decimals.
        """
        # Convert the raw voltage array to actual voltage considering Vs_voltage
        raw_value_array = (raw_value_array / self.__class__.Vs_voltage) * 4.7
        # Apply calibration offset and scale
        pressure_array = (raw_value_array * PRESSURE_TRANSDUCER_CALIBRATION[1]) + PRESSURE_TRANSDUCER_CALIBRATION[0]
        return pressure_array.round(2)

    async def get_raw_value(self) -> float:
        """
        Retrieve the raw voltage value from the LabJack and update Vs_voltage if necessary.

        Returns:
            float: The raw voltage reading.
        """
        # Check if Vs voltage needs to be read
        if self.__class__.Vs_pin:
            if time.time() - self.__class__.Vs_checked_time > 10:
                # Update Vs_voltage by reading from the Vs_pin
                self.__class__.Vs_voltage = await self.labjack.read(self.__class__.Vs_pin)
                self.__class__.Vs_checked_time = time.time()
                #self.logger.debug(f"Vs voltage: {self.__class__.Vs_voltage}")
        # Read the raw voltage value from the LabJack
        voltage = await self.labjack.read(self.pin)
        return voltage