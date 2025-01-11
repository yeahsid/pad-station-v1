from abc import ABC, abstractmethod
import logging
from enum import Enum
import asyncio
import numpy as np
import threading

class AbstractAnalogSensor:
    """
    Abstract base class for all analog sensors.

    Attributes:
        name (str): The name of the sensor.
        unit (str): The unit of measurement.
        streaming_enabled (bool): Flag to enable streaming of sensor data.
    """
    logger = logging.getLogger(__name__)

    def __init__(self, name: str, unit: str, streaming_enabled: bool):
        self.name = name
        self.unit = unit
        self.streaming_enabled = streaming_enabled
        self.is_streaming = False
        self.lock = threading.Lock()  # Lock for thread safety during streaming

        try:
            try:
                # Check for an existing event loop
                loop = asyncio.get_running_loop()
                loop.create_task(self.setup())  # Schedule setup in the running loop
            except RuntimeError:
                # If no loop is running, use asyncio.run()
                asyncio.run(self.setup())
            self.logger.info(f"Sensor {self.name} setup complete")
        except Exception as e:
            self.logger.error(f"Sensor {self.name} setup failed: {e}")
            raise e
    
    @abstractmethod
    async def setup(self):
        """Abstract method to setup the sensor."""
        pass

    def convert(self, raw_value: float | np.ndarray) -> float | np.ndarray:
        """
        Convert raw sensor data to meaningful units.

        Args:
            raw_value (float | np.ndarray): Raw sensor data.

        Returns:
            float | np.ndarray: Converted sensor data.
        """
        try:
            raw_value = float(raw_value)
        except ValueError:
            pass

        if isinstance(raw_value, float):
            return self.convert_single(raw_value)
        elif isinstance(raw_value, np.ndarray):
            return self.convert_array(raw_value.astype(float))
        else:
            raise TypeError("Unsupported type for raw_value")

    @abstractmethod
    def convert_single(self, raw_value: float) -> float:
        """Abstract method to convert a single raw value."""
        pass

    @abstractmethod
    def convert_array(self, raw_value_array: np.ndarray) -> np.ndarray:
        """Abstract method to convert an array of raw values."""
        pass

    @abstractmethod
    async def get_raw_value(self) -> float:
        """Abstract method to retrieve raw sensor data."""
        pass

    def read_stored_value(self) -> float:
        with self.lock:
            if self.is_streaming:
                return self.streaming_value
            else:
                raise ValueError("Attempted to read stored value of non-streaming sensor")

    async def read(self) -> float:
        """
        Read the current sensor value, either streaming or raw.

        Returns:
            float: The sensor value.
        """
        with self.lock:
            if self.is_streaming:
                return self.streaming_value if self.streaming_value else 0
        
        raw_value = await self.get_raw_value()
        return self.convert(raw_value)

    def set_streaming(self, value: float|None = None):
        """
        Enable streaming and set the streaming value.

        Args:
            value (float|None): The value to stream. Defaults to None.
        """
        with self.lock:
            self.is_streaming = True
            if value is not None:
                self.streaming_value = value

    def deactivate_streaming(self):
        """Disable streaming and clear the streaming value."""
        with self.lock:
            self.is_streaming = False
            self.streaming_value = None

class AbstractDigitalSensor:
    logger = logging.getLogger(__name__)

    def __init__(self, name: str):
        self.name = name
    
        try:
            try:
                # Check for an existing event loop
                loop = asyncio.get_running_loop()
                loop.create_task(self.setup())  # Schedule setup in the running loop
            except RuntimeError:
                # If no loop is running, use asyncio.run()
                asyncio.run(self.setup())
            self.logger.info(f"Sensor {self.name} setup complete")
        except Exception as e:
            self.logger.error(f"Sensor {self.name} setup failed: {e}")
            raise e
    
    @abstractmethod
    async def setup(self):
        """Abstract method to setup the sensor."""
        pass

    @abstractmethod
    async def read(self) -> Enum:
        """Abstract method to read the sensor state."""
        pass
