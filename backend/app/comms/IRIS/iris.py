"""
IRIS.py

Created on: 18/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS instance
"""


import iris_status
from iris_packet import IrisPacket
from iris_interface import IrisInterface
import asyncio



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
                tx_queue: asyncio.PriorityQueue,
                rx_queue: asyncio.PriorityQueue,
                interface: IrisInterface
                ):
        self.devID = devID
        self.tx_queue = tx_queue
        self.rx_queue = rx_queue
        self.interface = interface
        self.current_event_ID = 0
        self.stats = 0
    
    def irisSendRequest(self, event_notifier: asyncio.Event, request_packet: IrisPacket, response_packet: IrisPacket, response_payload_class, response_timeout: int):
        """
        Function for putting a request onto the tx queue to be shipped off by the hardware protocol.
        
        args: 
            event_notifier (event): The event to notify when the response to this request has arrived.
            request_packet (IrisPacket): the packet we're sending out
            response_packet (IrisPacket): used to check that the response was correct and to fill in the response payload
            response_timeout (int): how long we willin to wait

        returns:
            none
        
        Exceptions:
            IRIS_ERR_UNKKNOWN: If the response packet wasn't as expected
            IRIS_ERR_TIMEOUT: If the the response timed out
            

        """
        pass

    def irisSendResponse(self, packet: IrisPacket):
         """
        Function for putting a response onto the tx queue to be shipped off by the hardware protocol.
        
        args: 
            packet (IrisPacket): The packet to be shipped off as a response.

        returns:
            none
        
        Exceptions:
            IRIS_ERR_UNKKNOWN: If the response packet wasn't as expected
            IRIS_ERR_TIMEOUT: If the the response timed out
            

        """
        pass

    def irisSendMessage(self, packet: IrisPacket):
         """
        Function for putting a message onto the tx queue to be shipped off by the hardware protocol.
        
        args: 
            packet (IrisPacket): The packet to be shipped off as a message.

        returns:
            none
        
        Exceptions:
            IRIS_ERR_UNKKNOWN: If the response packet wasn't as expected
            IRIS_ERR_TIMEOUT: If the the response timed out
            

        """
        pass

    def irisRespondtoReceiveEvent(self, packet: IrisPacket):
         """
        Function for responding to a receive event, does different things based on the type of packet. 
        args: 
            packet (IrisPacket): The packet to be shipped off as a response.

        returns:
            none
        
        Exceptions:
            IRIS_ERR_UNKKNOWN: If the response packet wasn't as expected
            IRIS_ERR_TIMEOUT: If the the response timed out
            

        """
        pass

    def irisCallRespondFunction(Iris, packet: IrisPacket):
        """
        Function for actioning a request or message that has been received by calling the appropriate function.
        args: 
            packet (IrisPacket): The packet to be shipped off as a response.

        returns:
            none
        
        Exceptions:

        """
        pass

    def irisTransmit(self, transmitPacket: IrisPacket):
        self.interface.interfaceSendPacket(self,transmitPacket)

