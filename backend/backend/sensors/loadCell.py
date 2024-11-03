from dataclasses import dataclass
import logging
from backend.sensors.abstractSensors import AbstractAnalogSensor, extract_number_from_ain
from backend.config import LOAD_CELL_CALIBRATION

logger = logging.getLogger(__name__)

@dataclass
class LoadCell(AbstractAnalogSensor):
    name: str
    signal_pos: str
    signal_neg: str
    calibration: tuple[float, float] = LOAD_CELL_CALIBRATION
    tare_reading: float = 0.0

    def __post_init__(self):
        modbus_address = int(extract_number_from_ain(self.signal_pos)) * 2  # Convert signal_pos to Modbus address
        super().__init__(self.name, "N", modbus_address)

    async def setup(self):
        await self.labjack.write(f"{self.signal_pos}_RANGE", 0.01)
        await self.labjack.write(f"{self.signal_pos}_RESOLUTION_INDEX", 0)
        await self.labjack.write(f"{self.signal_pos}_NEGATIVE_CH", extract_number_from_ain(self.signal_neg))
        await self.labjack.write(f"{self.signal_pos}_SETTLING_US", 0)

    def convert(self, raw_value: float) -> float:
        force = raw_value * self.calibration[1] + self.calibration[0]
        force -= self.tare_reading
        return round(force, 3)

    async def get_raw_value(self) -> float:
        voltage = await self.labjack.read(self.signal_pos)
        return voltage

    async def tare(self):
        self.tare_reading = await self.read() + self.tare_reading
