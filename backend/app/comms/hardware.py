"""
This is a Python module named hardware.py that contains a class LabJackConnection for managing a connection to a LabJack device.
"""

# Import necessary modules
import logging
from typing import Optional, Callable
from labjack import ljm
from app.comms.exceptions import DeviceNotOpenError, LabJackError
import time

# Set up a logger for the module
logger = logging.getLogger(__name__)

# Define the LabJackConnection class


class LabJackConnection:
    """
    Represents a connection to a LabJack device.

    Attributes:
        handle: The handle to the LabJack device.

    Methods:
        __init__(): Initializes the LabJackConnection object and opens a connection to a LabJack device.
        __del__(): Closes the connection to the LabJack device when the object is destroyed.
        _access_pin(): Private method to access a pin on the LabJack device.
        write(): Writes a value to a pin on the LabJack device.
        read(): Reads a value from a pin on the LabJack device.
    """

    def __init__(self):
        """
        Initializes the LabJackConnection object and opens a connection to a LabJack device.

        Raises:
            DeviceNotOpenError: If the connection to the LabJack device fails.
        """
       # try:
        self.handle = ljm.openS("T7", "TCP", "192.168.0.5")
            # self.handle = ljm.openS("T7", "USB", "ANY")
        #self.handle = ljm.openS("T7", "ANY", "ANY")

        #except:
         #   logger.error("Failed to open device")
          #  raise DeviceNotOpenError("Failed to open device")

    def __del__(self):
        """
        Closes the connection to the LabJack device when the object is destroyed.
        """
        if hasattr(self, 'handle') and self.handle:
            ljm.close(self.handle)

    def _access_pin(self, pin: str, action: Callable, value: Optional[int] = None) -> int:
        """
        Private method to access a pin on the LabJack device.

        Args:
            pin: The name of the pin to access.
            action: The action to perform on the pin (read or write).
            value: The value to write to the pin (optional).

        Returns:
            The value read from the pin (for read actions) or the result of the write action.

        Raises:
            DeviceNotOpenError: If the connection to the LabJack device is not open.
            LabJackError: If an error occurs while accessing the pin.
        """
        if not hasattr(self, 'handle') or self.handle is None:
            logger.error("Device not open")
            raise DeviceNotOpenError("Device not open")
        try:
            if value is not None:
                return action(self.handle, pin, value)
            else:
                return action(self.handle, pin)
        except ljm.LJMError as e:
            logger.error(str(e))
            raise LabJackError(str(e))

    def write(self, pin: str, value: int):
        """
        Writes a value to a pin on the LabJack device.

        Args:
            pin: The name of the pin to write to.
            value: The value to write to the pin.
        """
        self._access_pin(pin, ljm.eWriteName, value)

    def read(self, pin: str) -> int:
        """
        Reads a value from a pin on the LabJack device.

        Args:
            pin: The name of the pin to read from.

        Returns:
            The value read from the pin.
        """
        val = self._access_pin(pin, ljm.eReadName)
        time.sleep(0.005)
        return val

if __name__ == "__main__":
	a = LabJackConnection()
	input("beep boop")
	a.write("CIO2", 1)
	input("beep boop")
