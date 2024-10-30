from enum import Enum

class BinaryPosition(Enum):
    OPEN = "open"
    CLOSE = "close"

class HanbayValveState(Enum):
    IN_POSITION = "in_position"
    MOVING = "moving"
    STALLED = "error"
    UNKNOWN_STATE = "unknown_state"

class HanbayValveEncodings:
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
