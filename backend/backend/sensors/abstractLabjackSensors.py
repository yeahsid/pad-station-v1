from backend.control.labjack import LabJack
from backend.sensors.abstractSensors import AbstractAnalogSensor

from abc import ABC


class AbstractAnalogSensorLJ(ABC, AbstractAnalogSensor):
    """
    Abstract base class for labjack specific analog sensors.

    Attributes:
        name (str): The name of the sensor.
        unit (str): The unit of measurement.
        streaming_enabled (bool): Flag to enable streaming of sensor data.
        streaming_address (int|None): Address for streaming data. See https://support.labjack.com/docs/3-1-modbus-map-t-series-datasheet.
    """

    def __init__(self, name: str, unit: str, streaming_enabled: bool, streaming_address: int|None = None):
        self.labjack = LabJack()
        self.streaming_address = streaming_address

        super().__init__(name, unit, streaming_enabled)
    
class AbstractDigitalSensorLJ(ABC):
    def __init__(self, name: str):
        self.labjack = LabJack()

        super().__init__(name)

def extract_number_from_ain(ain_string):
    """
    Extract the first integer found in a string representing an AIN pin.

    Args:
        ain_string (str): The AIN pin string (e.g., 'AIN13').

    Returns:
        int: The extracted number.

    Raises:
        ValueError: If no number is found in the string.
    """
    match = re.search(r'\d+', ain_string)
    if match:
        return int(match.group())
    else:
        raise ValueError("No number found in the string")
    