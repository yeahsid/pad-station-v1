from backend.papiris.iris import Iris
from backend.sensors.abstractSensors import AbstractAnalogSensor

from abc import ABC


class AbstractAnalogSensorMC(ABC, AbstractAnalogSensor):
    """
    Abstract base class for motor controller specific analog sensors.

    Attributes:
        name (str): The name of the sensor.
        unit (str): The unit of measurement.
        streaming_enabled (bool): Flag to enable streaming of sensor data.
        target_dev_id (int): The dev id of the target device
        target_sens_id (int): The id of the sensor on the target device
    """

    def __init__(self, name: str, unit: str, streaming_enabled: bool, target_dev_id: int, target_sens_id: int):
        self.iris = Iris()
        self.target_dev_id = target_dev_id
        self.target_sens_id = target_sens_id

        super().__init__(name, unit, streaming_enabled)
    
