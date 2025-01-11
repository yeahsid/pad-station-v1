from backend.util.config import FRONTEND_UPDATE_RATE
from backend.util.constants import BinaryPosition
from backend.sensors.abstractMotorControllerSensors import AbstractDigitalSensorMC
from backend.papiris.iris import iris_packet_definitions as packets
from backend.papiris.iris import IrisPacketPriority


class LimitSwitch(AbstractDigitalSensorMC):
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

        self.request_struct = packets.LIMIT_SWITCH_READ_RequestStruct()
        self.request_struct.switch_select = self.target_sens_id

    async def setup(self):
        """Setup method for PressureTransducerMC. No setup required."""
        pass  # No setup required for pressure transducer
    
    async def read(self) -> BinaryPosition:
        """
        Retrieve the pressure reading from the target device.

        Returns:
            float: The pressure reading.
        """

        response_struct: packets.LIMIT_SWITCH_READ_ResponseStruct
        
        _, response_struct = await self.iris.send_request(
            request_struct=self.request_struct,
            priority=IrisPacketPriority.IRIS_PACKET_PRIORITY_LOW,
            other_dev_id=self.target_dev_id,
            response_timeout=1 / FRONTEND_UPDATE_RATE
        )

        return BinaryPosition.CLOSE if response_struct.state == 0x01 else BinaryPosition.OPEN  # 1 == switch hit
