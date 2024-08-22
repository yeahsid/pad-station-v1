"""
IRIS_SERIAL.py

Created on: 22/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS serial interace
"""

from iris import Iris
from iris_interface import IrisInterface
import iris_status
import asyncio
import serial_asyncio
from iris_packet import IrisPacket


class IrisRS422(IrisInterface):
    """
    Represents the IRISRS422 interface class

    Attributes:
        Serial (serial): Iris' Serial instance.
        Port (str): The COM port the serial transceiver is connected to
        baudrate (int):

    Methods:
        __init__(self , port, baud): open serial port
        interfaceInit(iris):
        interfaceParsePacket(iris, packet):
        interfaceSendPacket(iris, packet):
    """

    def interfaceInit(iris: Iris):
        return super().interfaceInit()
    
    def interfaceParsePacket(iris: Iris, packet: IrisPacket):
        return super().interfaceParsePacket(packet)
    
    def interfaceSendPacket(iris, packet: IrisPacket):
        return super().interfaceSendPacket(packet)
    
