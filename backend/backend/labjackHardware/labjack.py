import logging
from typing import Optional, Callable
from labjack import ljm
from labjack.ljm import LJMError; 

class LabJack:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self._handle = ljm.openS("T7", "TCP", "192.168.0.5")

    def __del__(self):
        """
        Closes the connection to the LabJack device when the object is destroyed.
        """
        if hasattr(self, 'handle') and self._handle:
            ljm.close(self._handle)

    async def _access_pin(self, pin: str, action: Callable, value: Optional[int] = None) -> int:
        """
        Private method to access a pin on the LabJack device.

        Args:
            pin: The name of the pin to access.
            action: The action to perform on the pin (read or write).
            value: The value to write to the pin (optional).

        Returns:
            The value read from the pin (for read actions) or the result of the write action.

        Raises:
            LabJackError: If an error occurs while accessing the pin.
        """
        try:
            if value is not None:
                return action(self._handle, pin, value)
            else:
                return action(self._handle, pin)
        except ljm.LJMError as e:
            self.logger.error(str(e))
            raise e

    async def write(self, pin: str, value: int):
        """
        Writes a value to a pin on the LabJack device.

        Args:
            pin: The name of the pin to write to.
            value: The value to write to the pin.
        """
        await self._access_pin(pin, ljm.eWriteName, value)

    async def read(self, pin: str) -> int:
        """
        Reads a value from a pin on the LabJack device.

        Args:
            pin: The name of the pin to read from.

        Returns:
            The value read from the pin.
        """
        val = await self._access_pin(pin, ljm.eReadName)
        return val

