"""
IRIS_STATUS.py

Created on: 18/08/2024
Created by: Maisur Rahman

Enum for different statuses
"""

class IRIS_OK(Exception):
    pass

class IRIS_ERR_ARGUMENT_OUT_OF_RANGE(Exception):
    pass

class IRIS_ERR_TIMEOUT(Exception):
    pass

class IRIS_ERR_UNKNOWN(Exception):
    pass

class IRIS_ERR_PACKET_TYPE(Exception):
    pass
