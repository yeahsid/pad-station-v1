"""
IRIS packet definition file for inter-device communication. 
"""
from enum import Enum
from typing import Tuple


class packet_types(Tuple, Enum):
    dc_motor1_state = ("IRIS_PACKET_DC_MOTOR1_STATE", 118, 0, 6, "dc_motor1_state")
    


