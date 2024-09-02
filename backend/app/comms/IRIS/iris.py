"""
IRIS.py

Created on: 18/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS instance
"""


from iris_status import IRIS_ERR_ARGUMENT_OUT_OF_RANGE, IRIS_ERR_TIMEOUT, IRIS_ERR_UNKNOWN, IRIS_ERR_PACKET_TYPE, IRIS_OK
from iris_packet import IrisPacket, IRIS_NUM_EVENT_ID, IRIS_PAYLOAD_DATA_SIZE
from iris_interface import IrisInterface
from iris_event_handler import IrisEventTracker
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
                interface: IrisInterface
                ):
        self.devID = devID
        self.tx_queue = asyncio.PriorityQueue(IRIS_NUM_EVENT_ID)
        self.rx_queue = asyncio.PriorityQueue(IRIS_NUM_EVENT_ID)
        self.interface = interface
        self.current_event_ID = 0
        self.stats = 0
        self.event_tracker = dict.fromkeys(range(IRIS_NUM_EVENT_ID))    # someone needs to check this reaaaaaal bad
        self.event_to_packet = dict.fromkeys(range(IRIS_NUM_EVENT_ID))
    
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
        current_event = IrisEventTracker(event_notifier,response_timeout)
        self.event_tracker[request_packet.eventID] = current_event

        self.tx_queue.put(request_packet)

        try:
            asyncio.wait_for(event_notifier.wait(),response_timeout)

        except asyncio.TimeoutError:
            raise IRIS_ERR_TIMEOUT
        
        response_packet = self.event_to_packet[request_packet.eventID]
        #IrisPayloadToClass(response_packet.payload)

        

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
        self.tx_queue.put((packet.priority, packet))
        

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

        self.tx_queue.put((packet.priority, packet))
    
    def irisCallRespondFunction(self, packet: IrisPacket):
        """
        Function for actioning a request or message that has been received by calling the appropriate function.
        args: 
            packet (IrisPacket): The packet to be shipped off as a response.

        returns:
            none
        
        Exceptions:
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
        if (packet.messageNotService | packet.requestNotResponse):
            self.irisCallRespondFunction(packet)
        
        else:
            if packet.eventID in self.event_tracker:
                




    def irisTransmit(self, transmitPacket: IrisPacket):
        self.interface.interfaceSendPacket(self,transmitPacket)

