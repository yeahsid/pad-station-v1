from dataclasses import dataclass
import logging
import numpy as np
from backend.sensors.abstractSensors import AbstractAnalogSensor, extract_number_from_ain

logger = logging.getLogger(__name__)

@dataclass
class Thermocouple(AbstractAnalogSensor):
    name: str
    pin: str
    streaming_enabled: bool

    def __post_init__(self):
        modbus_address = extract_number_from_ain(self.pin) * 2  # Convert AIN to Modbus address
        super().__init__(self.name, "Celsius", self.streaming_enabled, modbus_address)

    async def setup(self):
        await self.labjack.write(f"{self.pin}_EF_INDEX", 22) # Type K thermocouple
        await self.labjack.write(f"{self.pin}_EF_CONFIG_A", 1) # Celsius
        await self.labjack.write(f"{self.pin}_EF_CONFIG_B", 60052) # MODBUS address of internal CJC sensor 
        await self.labjack.write(f"{self.pin}_EF_CONFIG_D", 1.0) # CJC Coefficient  
        await self.labjack.write(f"{self.pin}_EF_CONFIG_E", 0.0) # CJC Offset

    def convert_single(self, raw_value: float) -> float:
        return np.round(raw_value, 2)
    
    def convert_array(self, raw_value_array: np.ndarray) -> np.ndarray:
        return raw_value_array.round(2)

    async def get_raw_value(self) -> float:
        temperature = await self.labjack.read(f"{self.pin}_EF_READ_A")
        return temperature
