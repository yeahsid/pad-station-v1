from typing import Tuple
from dataclasses import dataclass
import mvp_packets

MAX_PACKET_SIZE = 8

@dataclass
class IRISPacket:

    def __init__(self, ):
        self.otherDevID: str
        self.packetID: Tuple[str, int, int, int, str]
        self.payload: list
        self.payloadLength: int
        self.requestNotResponse: bool

