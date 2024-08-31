"""
IRIS_SERIAL.py

Created on: 22/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS serial interace
"""

from iris import Iris
from iris_interface import IrisInterface
import asyncio
import serial_asyncio
from iris_packet import IrisPacket


"""
wall of text time:

isntead of using serial asyncio, make a task that continually reads one byte from the com port
if it finds a start of frame bit (0xC0) it starts reading the header. Once you have the payload
length in the header, set a loop to keep reading and storing the bytes received based on the length
of the payload

async def serial_read_task()
    data = serial.read(1)
    if data.hex() = '0xC0':
        serial_packet = serial_packet()
        




"""




class IrisRS422(IrisInterface):
    """
    Represents the IRISRS422 interface class

    Attributes:
        Port (str): The COM port the serial transceiver is connected to
        baudrate (int):
        rxQueue (queue):
        txQueue (queue):
        loop (loop):
        iris (Iris):

    Methods:
        __init__(self , port, baud): open serial port
        interfaceInit(iris):
        interfaceParsePacket(iris, packet):
        interfaceSendPacket(iris, packet):
    """
    def __init__(
            self,
            Port: str,
            baudrate: int,
            rxQueue: asyncio.PriorityQueue,
            txQueue: asyncio.PriorityQueue,
    ):
        self.Port = Port
        self.baudrate = baudrate
        self.rxQueue = rxQueue
        self.txQueue = txQueue
        self.interfaceInit(self, Iris)

    def interfaceInit(self, iris: Iris):
        iris_port = serial_asyncio.create_serial_connection(self.loop, HardwareProtocol, self.Port, self.baudrate)
        transport, protocol = self.loop.run_until_complete(iris_port)
    
    def interfaceParsePacket(iris: Iris, packet: IrisPacket):
        return super().interfaceParsePacket(packet)
    
    def interfaceSendPacket(iris, packet: IrisPacket):
        return super().interfaceSendPacket(packet)
    

class HardwareProtocol(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self._transport = None

    def connection_made(self, transport):
        self._transport = transport
        self._transport.serial.rts = False
        

    def data_received(self, data):
        #split the data into the necessary bits
        split_data = data.split()

        #init an IRIS Packet
        new_packet = IrisPacket(split_data)

        #notify iris a receive event happened.
        rxCallback.set()        

    def connection_lost(self, exc):
        pass

    def pause_writing(self):
        pass

    def resume_writing(self):
        pass