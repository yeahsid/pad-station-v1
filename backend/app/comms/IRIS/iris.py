"""
IRIS.py

Created on: 18/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS instance
"""

from queue import PriorityQueue

import iris_status
from iris_packet import IrisPacket
from iris_interface import IrisInterface



class Iris() : 
    """
    Represents an IRIS instance

    Attributes:

        devID (int): The ID of the device this instance of IRIS is running on.
        currentEventID (int): The current event's ID.
        txQueue (queue)
        rxQueue (queue)
        interface (IrisInterface): The hardware interface helper class.
        stats (int): No. of timeouts occured in this instance of IRIS

    Methods:
        __init__(): Initialise the IRIS instance.
        irisSendRequest(Iris, eventnotifier, IrisPacket, IrisPacket, int): 
        irisSendResponse(Iris, IrisPacket):
        irisSendMessage(Iris, IrisPacket):
        irisRespondtoReceiveEvent(Iris, IrisPacket):
        irisCallRespondFunction(Iris, IrisPacket): 
    """

    def __init__(self,
                devID: int,
                txQueue: PriorityQueue,
                rxQueue: PriorityQueue,
                interface: IrisInterface
                ):
        self.devID = devID
        self.txQueue = txQueue
        self.rxQueue = rxQueue
        self.interface = interface
        self.currentEventID = 0
        self.stats = 0
    
    def irisSendRequest(self, eventNotifier, request_packet: IrisPacket, response_packet: IrisPacket, timeout: int):
        pass

    def irisSendResponse(self, packet: IrisPacket):
        pass

    def irisSendMessage(self, packet: IrisPacket):
        pass

    def irisRespondtoReceiveEvent(self, packet: IrisPacket):
        pass

    def irisCallRespondFunction(Iris, packet: IrisPacket):
        pass

    def irisTransmit(self, transmitPacket: IrisPacket):
        self.interface.interfaceSendPacket(self,transmitPacket)

