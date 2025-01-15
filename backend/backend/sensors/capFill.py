from backend.util.config import FRONTEND_UPDATE_RATE
from backend.sensors.abstractMotorControllerSensors import AbstractAnalogSensorMC
from backend.papiris.iris import CAP_FILL_READING_MessageStruct
from backend.papiris.iris import IrisPacket

import numpy as np


class CapFill(AbstractAnalogSensorMC):
    """
    Represents a Pressure Transducer sensor for measuring pressure.

    Attributes:
        name (str): The name of the sensor.
        pin (str): The LabJack pin connected to the sensor.
        streaming_enabled (bool): Flag to enable streaming of sensor data.
        calibration (tuple): Calibration offset and scale.
        tare_reading (float): Tare value to zero the sensor.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the PressureTransducer sensor with Modbus address."""
        super().__init__(*args, **kwargs)
        self._value = -1

        self.iris.message_id_to_respond_function[CAP_FILL_READING_MessageStruct().get_id()] = self._message_hook

    async def setup(self):
        """Setup method for PressureTransducerMC. No setup required."""
        pass  # No setup required for pressure transducer
    
    async def _message_hook(self, iris, packet: IrisPacket, struct: CAP_FILL_READING_MessageStruct):
        self._value = struct.reading

    async def get_raw_value(self) -> float:
        """
        Retrieve the pressure reading from the target device.

        Returns:
            float: The pressure reading.
        """

        return self._value

    def convert_single(self, raw_value: float) -> float:
        return raw_value  # conversions definitely required

    def convert_array(self, raw_value_array: np.ndarray) -> np.ndarray:
        return raw_value_array  # conversions definitely required
