from backend.util.config import FRONTEND_UPDATE_RATE
from backend.sensors.abstractMotorControllerSensors import AbstractAnalogSensorMC
from backend.papiris.iris import iris_packet_definitions as packets
from backend.papiris.iris import IrisPacketPriority

import numpy as np


class ThermocoupleMC(AbstractAnalogSensorMC):
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

        self.request_struct = packets.THERMOCOUPLE_READ_RequestStruct()
        self.request_struct.tc_select = self.target_sens_id

    async def setup(self):
        """Setup method for PressureTransducerMC. No setup required."""
        pass  # No setup required for pressure transducer
    
    async def get_raw_value(self) -> float:
        """
        Retrieve the pressure reading from the target device.

        Returns:
            float: The pressure reading.
        """

        response_struct: packets.THERMOCOUPLE_READ_ResponseStruct
        
        _, response_struct = await self.iris.send_request(
            request_struct=self.request_struct,
            priority=IrisPacketPriority.IRIS_PACKET_PRIORITY_LOW,
            other_dev_id=self.target_dev_id,
            response_timeout=1 / FRONTEND_UPDATE_RATE
        )

        return response_struct.tc_temp

    def convert_single(self, raw_value: float) -> float:
        return raw_value  # no conversions required

    def convert_array(self, raw_value_array: np.ndarray) -> np.ndarray:
        return raw_value_array  # no conversions required
