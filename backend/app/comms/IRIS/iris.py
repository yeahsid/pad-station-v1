from typing import Tuple
from dataclasses import dataclass

MAX_PACKET_SIZE = 8

@dataclass
class IRISPacket:

    otherDevID: str
    packetID: Tuple[str, int, int, int, str]
    payload: list
    payloadLength: int
    requestNotResponse: bool


class IRIS:
    pass