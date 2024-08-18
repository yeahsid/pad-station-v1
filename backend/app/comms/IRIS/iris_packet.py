"""
IRIS_PACKET.py

Created on: 18/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS packet
"""
from mvp_packets import packet_types
from dataclasses import dataclass
from enum import Enum

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
        eventID (int): Specific identifier for this message. 
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

    def __init__(self, priority: IrisPacketPriority, eventID: int, ):
        pass