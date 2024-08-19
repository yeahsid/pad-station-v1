"""
IRIS_PACKET.py

Created on: 18/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS packet
"""
from mvp_packets import packet_types
from dataclasses import dataclass
from enum import Enum
from iris import Iris
from iris_status import IrisStatus

#The number of different events that can occur at any time
IRIS_NUM_EVENT_ID = 8

#The length of the payload sent over serial.
IRIS_PAYLOAD_DATA_SIZE = 8

class IrisPacketPriority(Enum,int):
    IRIS_PACKET_PRIORITY_LOW = 0,
    IRIS_PACKET_PRIORITY_MEDIUM = 1,
    IRIS_PACKET_PRIORITY_HIGH = 2,
    IRIS_PACKET_PRIORITY_REALTIME = 3


#define a class for a packet:
class IrisPacket:
    """
    Represents an IRIS packet

    Attributes:

        # Packet Fields
        priority (IrisPacketPriority): The priority of the message when it is sent or received to the tx or rx queue.
        packetID (packet_types): The ID of the packet being sent from the packet library
        payload: The data to be sent in the message
        payloadLength (int): Length of the payload
        messageNotService (bool): Whether or not the packet is a simple broadcast or a request.

        # Service Fields
        otherDevID (int): The ID of the receiving node of the message
        requestNotResponse (bool): Whether or not the packet will be a request or a response. Represents the requestnotresponse bit in an IRIS header.
        timestamp (int): the timestamp of the packet. 

    Methods:
        __init__(): Creates an IRIS packet with the required fields.
    """

    def __init__(self,
                iris: Iris,
                priority: IrisPacketPriority,
                packetid: packet_types,
                payload,
                payloadlength: int,
                messagenotservice: bool,
                otherDevID: int,
                requestNotResponse: bool,
                ):
        self.priority = priority
        self.eventID = (iris.currentEventID) + 1 % 8
        self.packetID = packetid
        self.payloadLength = payloadlength
        self.messageNotService = messagenotservice
        self.requestNotResponse = requestNotResponse
        self.otherDevID = otherDevID
        self.payload = payload  # gonna have to split this up into 8 byte chunks for multi-frame transmissions.
        #self.timestamp = getTime()

    def __new__():
        return IrisStatus.IRIS_OK   #lol check if this is even what we're meant to do
    
