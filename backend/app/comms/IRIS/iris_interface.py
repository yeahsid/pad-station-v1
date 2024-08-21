"""
IRIS_INTERFACE.py

Created on: 21/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS interface
"""

from iris import Iris
import iris_packet
from abc import ABC, abstractmethod

class IrisInterface(ABC):
    """
    Represents the hardware interface for IRIS to call.

    Methods:

        interfaceInit(): Abstract method to initialise the hardware interface.
        interfaceParsePacket(): Abstract method to fill construct an IRIS packet from received data.
        interfaceSendPacket(): Abstract method to send an IRIS packet using the hardware interface.
    """
    @abstractmethod
    def interfaceInit(iris: Iris):
        pass

    @abstractmethod
    def interfaceParsePacket(iris: Iris, packet: iris_packet):
        pass

    def interfaceSendPacket(iris, packet: iris_packet):
        pass
