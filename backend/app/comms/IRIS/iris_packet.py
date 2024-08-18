from typing import Tuple
from dataclasses import dataclass
from mvp_packets import packet_types

MAX_PACKET_SIZE = 8

@dataclass
class IRISPacket:

    def __init__(self, packet_type: packet_types):
        self.otherDevID: str
        self.packetID = packet_type
        self.payload: list
        self.payloadLength: int
        self.requestNotResponse: bool

