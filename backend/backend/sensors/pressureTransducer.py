from dataclasses import dataclass
import asyncio
import logging
from backend.sensors.abstractSensors import AbstractAnalogSensor
from backend.util.config import PRESSURE_TRANSDUCER_CALIBRATION, PRESSURE_TRANSDUCER_READ_VS, LabJackPeripherals
from backend.sensors.abstractSensors import extract_number_from_ain
import numpy as np
import time



class PressureTransducer(AbstractAnalogSensor):
    # Static class variables
    Vs_voltage: float = 4.7
    Vs_checked_time = time.time()
    Vs_pin: str = LabJackPeripherals.PRESSURE_TRANSDUCER_Vs_PIN.value if PRESSURE_TRANSDUCER_READ_VS else None

    def __init__(self, name: str, pin: str, streaming_enabled: bool):
        self.name = name
        self.pin = pin
        self.streaming_enabled = streaming_enabled

        modbus_address = extract_number_from_ain(self.pin) * 2 # Convert AIN to Modbus address
        super().__init__(self.name, "Bar", self.streaming_enabled, modbus_address)

        self.logger = logging.getLogger(__name__)

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
        # Check if Vs voltage needs to be read
        if self.__class__.Vs_pin:
            if time.time() - self.__class__.Vs_checked_time > 10:
                self.__class__.Vs_voltage = await self.labjack.read(self.__class__.Vs_pin)
                self.__class__.Vs_checked_time = time.time()
                #self.logger.debug(f"Vs voltage: {self.__class__.Vs_voltage}")
        # Read the raw voltage value from the LabJack
        voltage = await self.labjack.read(self.pin)
        return voltage