"""
IRIS_STATUS.py

Created on: 18/08/2024
Created by: Maisur Rahman

Enum for different statuses
"""

from enum import Enum

class IrisStatus(Enum):
    IRIS_OK = 0
    IRIS_ERR_ARGUMENT_OUT_OF_RANGE = 1
    IRIS_ERR_TIMEOUT = 2
    IRIS_ERR_UNKNOWN = 3
    IRIS_ERR_PACKET_TYPE = 4

def IRIS_RETURN_ON_ERROR(status):
    if status != IrisStatus.IRIS_OK:
        return status
    else:
        pass