from backend.util.config import FRONTEND_UPDATE_RATE
from papiris import iris
from papiris.iris.packet_types import *


class PressureTransducerMC:
    """
    Represents a Pressure Transducer sensor for measuring pressure.

    Attributes:
        name (str): The name of the sensor.
        pin (str): The LabJack pin connected to the sensor.
        streaming_enabled (bool): Flag to enable streaming of sensor data.
        calibration (tuple): Calibration offset and scale.
        tare_reading (float): Tare value to zero the sensor.
    """

    def __init__(self, name: str, iris_instance: iris.Iris, target_device_id: int, target_pt_id: int):
        """Initialize the PressureTransducer sensor with Modbus address."""
        self.name = name
        self.iris = iris_instance
        self.device_dev_id = target_device_id
        self.request_struct = PRESSURE_READ_RequestStruct()
        self.request_struct.pt_select = target_pt_id

    async def setup(self):
        """Setup method for PressureTransducer. No setup required."""
        pass  # No setup required for pressure transducer

    async def get_reading(self) -> float:
        """
        Retrieve the pressure reading from the target device.

        Returns:
            float: The pressure reading.
        """

        response_struct: PRESSURE_READ_ResponseStruct
        _, response_struct = self.iris.send_request(
            request_struct=self.request_struct,
            priority=iris.IrisPacketPriority.IRIS_PACKET_PRIORITY_LOW,
            other_dev_id=self.device_dev_id,
            response_timeout=1 / FRONTEND_UPDATE_RATE
        )

        return response_struct.pressure
