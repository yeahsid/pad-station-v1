from backend.util.constants import BinaryPosition, DCMotorState
from backend.sensors.abstractMotorControllerSensors import AbstractDigitalSensorMC
from backend.sensors.limitSwitchMC import LimitSwitch


class DcMotorStateSensor(AbstractDigitalSensorMC):
    """
    Represents a Pressure Transducer sensor for measuring pressure.

    Attributes:
        name (str): The name of the sensor.
        pin (str): The LabJack pin connected to the sensor.
        streaming_enabled (bool): Flag to enable streaming of sensor data.
        calibration (tuple): Calibration offset and scale.
        tare_reading (float): Tare value to zero the sensor.
    """

    def __init__(self, name: str, ls_open: LimitSwitch, ls_closed: LimitSwitch):
        """Initialize the PressureTransducer sensor with Modbus address."""

        self.open_limit_switch = ls_open
        self.closed_limit_switch = ls_closed

        super().__init__(name)

    async def setup(self):
        """Setup method for PressureTransducerMC. No setup required."""
        pass  # No setup required for pressure transducer
    
    async def read(self) -> DCMotorState:
        """
        Retrieve the pressure reading from the target device.

        Returns:
            float: The pressure reading.
        """

        if self.open_limit_switch.read() == BinaryPosition.CLOSE:
            return DCMotorState.OPEN
        elif self.closed_limit_switch.read() == BinaryPosition.CLOSE:
            return DCMotorState.CLOSE
        else:
            return DCMotorState.INTERMEDIATE
