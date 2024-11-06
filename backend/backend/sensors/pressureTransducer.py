from dataclasses import dataclass
import asyncio
import logging
from backend.sensors.abstractSensors import AbstractAnalogSensor
from backend.util.config import PRESSURE_TRANSDUCER_CALIBRATION, PRESSURE_TRANSDUCER_READ_VS, LabJackPeripherals
from backend.sensors.abstractSensors import extract_number_from_ain
import numpy as np

logger = logging.getLogger(__name__)

class PressureTransducer(AbstractAnalogSensor):
    # Static class variables
    Vs_voltage: float = 4.7
    Vs_pin: str = LabJackPeripherals.PRESSURE_TRANSDUCER_Vs_PIN if PRESSURE_TRANSDUCER_READ_VS else None
    _instances: list = []
    _labjack = None

    def __init__(self, name: str, pin: str, streaming_enabled: bool):
        self.name = name
        self.pin = pin
        self.streaming_enabled = streaming_enabled
        # Add instance to class list
        self.__class__._instances.append(self)
        # Store labjack reference at class level on first init
        if not self.__class__._labjack and hasattr(self, 'labjack'):
            self.__class__._labjack = self.labjack

    def __post_init__(self):
        modbus_address = extract_number_from_ain(self.pin) * 2 # Convert AIN to Modbus address
        super().__init__(self.name, "Bar", self.streaming_enabled, modbus_address)

    async def setup(self):
        pass  # No setup required for pressure transducer

    def convert_single(self, raw_value: float) -> float:
        # Convert the raw voltage value to pressure
        raw_value = (raw_value / self.__class__.Vs_voltage) * 4.7
        pressure = (raw_value * PRESSURE_TRANSDUCER_CALIBRATION[1]) + PRESSURE_TRANSDUCER_CALIBRATION[0]
        return np.round(pressure, 2)
    
    def convert_array(self, raw_value_array: np.ndarray) -> np.ndarray:
        # Convert the raw voltage array to pressure
        raw_value_array = (raw_value_array / self.__class__.Vs_voltage) * 4.7
        pressure_array = (raw_value_array * PRESSURE_TRANSDUCER_CALIBRATION[1]) + PRESSURE_TRANSDUCER_CALIBRATION[0]
        return pressure_array.round(2)

    async def get_raw_value(self) -> float:
        # Read the raw voltage value from the LabJack
        voltage = await self.labjack.read(self.pin)
        return voltage

    @classmethod
    def is_any_streaming(cls) -> bool:
        """Check if any pressure transducer instance is streaming"""
        return any(instance.streaming_enabled for instance in cls._instances)

    @classmethod
    async def poll_vs_pin(cls):
        """Poll Vs pin every 10s if it exists and no instances are streaming"""
        while True:
            if cls.Vs_pin and cls._labjack and not cls.is_any_streaming():
                try:
                    cls.Vs_voltage = await cls._labjack.read(cls.Vs_pin)
                    logger.debug(f"Updated Vs_voltage: {cls.Vs_voltage}")
                except Exception as e:
                    logger.error(f"Failed to poll Vs pin: {e}")
            await asyncio.sleep(10)

# Start polling the Vs pin
asyncio.create_task(PressureTransducer.poll_vs_pin())