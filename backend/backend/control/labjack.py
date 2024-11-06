import logging
from typing import Optional, Callable
from labjack import ljm
from labjack.ljm import LJMError
import numpy as np
from datetime import datetime, timedelta
from backend.util.config import TARGET_SCAN_RATE, FRONTEND_UPDATE_RATE

class LabJack:
    """
    Singleton class to interface with the LabJack device for hardware control and data acquisition.
    
    Attributes:
        logger (logging.Logger): Logger for the class.
        _handle (int): Handle for the LabJack device.
        real_scan_rate (float): The actual scan rate achieved by the LabJack device.
        next_read_start_time (datetime): The start time for the next read operation.
        streaming_addresses (list[int]): The MODBUS addresses of the pins being streamed.
    """
    logger = logging.getLogger(__name__)
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of LabJack exists (Singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super(LabJack, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the LabJack device connection if not already initialized.
        """
        if not hasattr(self, '_initialized'):
            self._handle = ljm.openS("T7", "TCP", "192.168.0.5")
            self.logger.info("LabJack device connected")
            self.real_scan_rate = None
            self.next_read_start_time = None
            self.streaming_addresses = None
            self._initialized = True

    def __del__(self):
        """
        Closes the connection to the LabJack device when the object is destroyed.
        """
        if hasattr(self, '_handle') and self._handle:
            ljm.close(self._handle)

    async def _access_pin(self, pin: str, action: Callable, value: Optional[int] = None) -> int:
        """
        Private method to access a pin on the LabJack device.
        
        Args:
            pin (str): The name of the pin to access.
            action (Callable): The action to perform on the pin (read or write).
            value (Optional[int]): The value to write to the pin (optional).
        
        Returns:
            int: The value read from the pin (for read actions) or the result of the write action.
        
        Raises:
            LJMError: If an error occurs while accessing the pin.
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
            pin (str): The name of the pin to write to.
            value (int): The value to write to the pin.
        """
        await self._access_pin(pin, ljm.eWriteName, value)

    async def read(self, pin: str) -> int | float:
        """
        Reads a value from a pin on the LabJack device.
        
        Args:
            pin (str): The name of the pin to read from.
        
        Returns:
            int | float: The value read from the pin.
        """
        val = await self._access_pin(pin, ljm.eReadName)
        return val
    
    def start_stream(self, addresses: list[int]) -> float:
        """
        Starts streaming data from the LabJack device.
        
        Args:
            addresses (list[int]): The MODBUS addresses of the pins to stream data from. 
                See https://support.labjack.com/docs/3-1-modbus-map-t-series-datasheet for address mapping.
        
        Returns:
            float: The actual scan rate achieved by the LabJack device.
        
        Raises:
            LJMError: If an error occurs while starting the stream.
        """
        try:
            # Calculate the number of scans per read based on target and frontend rates
            scans_per_read = TARGET_SCAN_RATE // FRONTEND_UPDATE_RATE
            real_scan_rate: float = ljm.eStreamStart(
                handle=self._handle, 
                scansPerRead=scans_per_read, 
                numAddresses=len(addresses),
                aScanList=addresses,
                scanRate=TARGET_SCAN_RATE
            )
            self.real_scan_rate = real_scan_rate
            self.next_read_start_time = datetime.now()
            self.streaming_addresses = addresses
            self.logger.debug(f"Streaming started with scan rate: {real_scan_rate}")
            return real_scan_rate
                
        except LJMError as e:
            self.logger.error(str(e))
            raise e
        
    def read_stream(self) -> np.ndarray:
        """
        Reads streaming data from the LabJack device.
        
        Returns:
            np.ndarray: The streaming data read from the LabJack device with timestamps.
                - Each row corresponds to a scan.
                - The first column contains the timestamps for each scan.
                - Subsequent columns contain data for each channel as per `self.streaming_addresses`.
        
        Raises:
            ValueError: If the number of data points is not a multiple of the number of channels.
            LJMError: If an error occurs while reading the stream.
        """
        try:
            # Retrieve streaming data and backlog information from LabJack
            data, deviceScanBacklog, ljmScanBacklog = ljm.eStreamRead(self._handle)
            self.logger.debug(f"Device scan backlog: {deviceScanBacklog}, LJM scan backlog: {ljmScanBacklog}")
            
            # Determine the number of channels being streamed
            num_channels = len(self.streaming_addresses)
            
            # Validate that the data length matches expected channels
            if len(data) % num_channels != 0:
                raise ValueError("Number of data points is not a multiple of the number of channels")
            num_scans = len(data) // num_channels

            # Reshape the flat data array into a 2D array with scans and channels
            data = np.array(data).reshape((num_scans, num_channels))

            # Generate precise timestamps for each scan based on the scan rate
            timestamps = [
                self.next_read_start_time + timedelta(seconds=i / self.real_scan_rate) 
                for i in range(num_scans)
            ]
            self.next_read_start_time = timestamps[-1] + timedelta(seconds=1 / self.real_scan_rate)

            # Combine timestamps with the sensor data
            data_with_timestamps = np.column_stack((timestamps, data))
            return data_with_timestamps
        except LJMError as e:
            self.logger.error(str(e))
            raise e
        
    def stop_stream(self):
        """
        Stops streaming data from the LabJack device.
        
        Raises:
            LJMError: If an error occurs while stopping the stream.
        """
        try:
            ljm.eStreamStop(self._handle)
        except LJMError as e:
            self.logger.error(str(e))
            raise e
