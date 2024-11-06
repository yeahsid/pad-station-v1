"""
This module defines constants and enumerations used across the backend of the PadStation application.
"""

from enum import Enum

class BinaryPosition(Enum):
    """Enumeration for binary positions."""
    OPEN = 1
    CLOSE = 0

class DCMotorState(Enum):
    """Enumeration for DC motor states."""
    OPEN = 1
    CLOSE = 0
    INTERMEDIATE = -1

class HanbayValveState(Enum):
    """Enumeration for Hanbay valve states."""
    IN_POSITION = 0
    MOVING = 1
    STALLED = -1
    UNKNOWN_STATE = -2

class HanbayValveEncodings:
    """Encodings for Hanbay valve input and output states."""
    input_high_high_open = {
        BinaryPosition.OPEN: (1, 1),
        BinaryPosition.CLOSE: (1, 0),
    }
    input_high_low_open = {
        BinaryPosition.OPEN: (1, 0),
        BinaryPosition.CLOSE: (1, 1),
    }
    output = {
        (0, 0): HanbayValveState.IN_POSITION,
        (1, 0): HanbayValveState.MOVING,
        (0, 1): HanbayValveState.STALLED,
        (1, 1): HanbayValveState.UNKNOWN_STATE,
    }
