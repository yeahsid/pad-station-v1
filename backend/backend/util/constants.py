from enum import Enum

class BinaryPosition(Enum):
    OPEN = 1
    CLOSE = 0

class DCMotorState(Enum):
    OPEN = 1
    CLOSE = 0
    INTERMEDIATE = -1

class HanbayValveState(Enum):
    IN_POSITION = 0
    MOVING = 1
    STALLED = -1
    UNKNOWN_STATE = -2

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
