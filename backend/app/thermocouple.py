from collections import deque
from dataclasses import dataclass
import asyncio

import logging
from app.hardware import LabJackConnection
from app.exceptions import ThermocoupleSensorError
from app.config import LABJACK_PINS

logger = logging.getLogger(__name__)

@dataclass
class Thermocouple:
    thermo_pin: str

class ThermocoupleSensor:
    """
    Represents a thermocouple sensor that measures temperature using LabJackConnection.

    Attributes:
        thermocouples (dict): A dictionary of thermocouples, where the keys are the names of the thermocouples
            and the values are instances of the Thermocouple class.
        labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
    """

    def __init__(self, labjack: LabJackConnection, filter_size: int = 10):
        """
        Initializes a ThermocoupleSensor object.

        Args:
            labjack (LabJackConnection): An instance of the LabJackConnection class used to communicate with the LabJack device.
        """
        self.thermocouples = {
            "engine": Thermocouple(LABJACK_PINS["thermocouple_engine"]),
        }
        self.labjack = labjack
        self.filter_size = filter_size
        self.thermocouple_readings = {name: deque(
            maxlen=filter_size) for name in self.thermocouples}
        self.thermocouple_sums = {name: 0 for name in self.thermocouples}

    def _get_thermocouple(self, thermocouple_name: str) -> Thermocouple:
        """
        Retrieves the specified thermocouple.

        Args:
            thermocouple_name (str): The name of the thermocouple.

        Returns:
            Thermocouple: The specified thermocouple.

        Raises:
            ThermocoupleSensorError: If the specified thermocouple is not found.
        """
        try:
            return self.thermocouples[thermocouple_name]
        except KeyError:
            logger.error("Thermocouple not found")
            raise ThermocoupleSensorError("Thermocouple not found")

    def get_thermocouple_temperature(self, thermocouple_name: str) -> float:
        """
        Get the temperature reading from a thermocouple.

        Args:
            thermocouple_name (str): The name of the thermocouple.

        Returns:
            float: The temperature reading in degrees Celsius.
        """
        thermocouple = self._get_thermocouple(thermocouple_name)
        temperature = self.labjack.read(thermocouple.thermo_pin)

        EF_INDEX = 22       # feature index for type K thermocouple
        EF_CONFIG_A = 1     # Celsius units
        EF_CONFIG_B = 60052 # TEMPERATURE_DEVICE_K for CJC address
        EF_CONFIG_D = 1.0   # slope for CJC reading
        EF_CONFIG_E = 0.0   # offset for CJC reading

        self.labjack.write(f"{thermocouple.thermo_pin}_EF_INDEX", EF_INDEX)
        self.labjack.write(f"{thermocouple.thermo_pin}_EF_CONFIG_A", EF_CONFIG_A)
        self.labjack.write(f"{thermocouple.thermo_pin}_EF_CONFIG_B", EF_CONFIG_B)
        self.labjack.write(f"{thermocouple.thermo_pin}_EF_CONFIG_D", EF_CONFIG_D)
        self.labjack.write(f"{thermocouple.thermo_pin}_EF_CONFIG_E", EF_CONFIG_E)
        
        temperature = self.labjack.read(f"{thermocouple.thermo_pin}_EF_READ_A")

        return temperature

    async def thermocouple_datastream(self, thermocouple_name: str):
        """
        Creates a data stream of temperature readings from the specified thermocouple.

        Args:
            thermocouple_name (str): The name of the thermocouple.

        Yields:
            float: The next temperature reading from the specified thermocouple.
        """
        while True:
            yield self.get_thermocouple_temperature(thermocouple_name)