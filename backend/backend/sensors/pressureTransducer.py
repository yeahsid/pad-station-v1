from dataclasses import dataclass
import asyncio
import logging
from backend.sensors.abstractSensors import AbstractAnalogSensor
from backend.util.config import PRESSURE_TRANSDUCER_CALIBRATION
from backend.sensors.abstractSensors import extract_number_from_ain

logger = logging.getLogger(__name__)

@dataclass
class PressureTransducer(AbstractAnalogSensor):
    name: str
    pin: str

    def __post_init__(self):
        modbus_address = extract_number_from_ain(self.pin) * 2 # Convert AIN to Modbus address
        super().__init__(self.name, "Bar", modbus_address)

    async def setup(self):
        pass  # No setup required for pressure transducer

    def convert(self, raw_value: float) -> float:
        # Convert the raw voltage value to pressure
        pressure = (raw_value * PRESSURE_TRANSDUCER_CALIBRATION[1]) + PRESSURE_TRANSDUCER_CALIBRATION[0]
        return round(pressure, 2)

    async def get_raw_value(self) -> float:
        # Read the raw voltage value from the LabJack
        voltage = await self.labjack.read(self.pin)
        return voltage