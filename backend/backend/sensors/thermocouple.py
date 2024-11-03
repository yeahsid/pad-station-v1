from dataclasses import dataclass
import logging
from backend.sensors.abstractSensors import AbstractAnalogSensor, extract_number_from_ain

logger = logging.getLogger(__name__)

@dataclass
class Thermocouple(AbstractAnalogSensor):
    name: str
    pin: str

    def __post_init__(self):
        modbus_address = extract_number_from_ain(self.pin) * 2  # Convert AIN to Modbus address
        super().__init__(self.name, "Celsius", modbus_address)

    async def setup(self):
        await self.labjack.write(f"{self.pin}_EF_INDEX", 22) # Type K thermocouple
        await self.labjack.write(f"{self.pin}_EF_CONFIG_A", 1) # Celsius
        await self.labjack.write(f"{self.pin}_EF_CONFIG_B", 60052) # MODBUS address of internal CJC sensor 
        await self.labjack.write(f"{self.pin}_EF_CONFIG_D", 1.0) # CJC Coefficient  
        await self.labjack.write(f"{self.pin}_EF_CONFIG_E", 0.0) # CJC Offset

    def convert(self, raw_value: float) -> float:
        return round(raw_value, 2)

    async def get_raw_value(self) -> float:
        temperature = await self.labjack.read(f"{self.pin}_EF_READ_A")
        return temperature
