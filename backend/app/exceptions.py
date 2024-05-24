# Define a custom exception for when a device is not open
class DeviceNotOpenError(Exception):
    """
    Exception raised when attempting to perform an operation on a device that is not open.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Device is not open."):
        self.message = message
        super().__init__(self.message)


# Define a custom exception for when a valve is not found


class ValveNotFoundError(Exception):
    pass


# Define a custom exception for when there is an error with the LabJack device


class ServoNotFoundError(Exception):
    pass


class LabJackError(Exception):
    pass


class PressureSensorError(Exception):
    pass


class LoadCellError(Exception):
    pass

class MotorError(Exception):
    pass