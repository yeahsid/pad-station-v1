from dataclasses import dataclass
import logging
from app.hardware import LabJackConnection
from app.exceptions import LoadCellError
from app.config import LABJACK_PINS

logger = logging.getLogger(__name__)


@dataclass
class LoadCell:
    feedback_pin1: str
    feedback_pin2: str


class LoadCellSensor:
    """
    A class that controls load cell using a LabJackConnection.

    Attributes:
        load cell (dict): A dictionary of load cells with load cell names as keys and load cell objects as values.
        labjack (LabJackConnection): An instance of LabJackConnection used for communication with the LabJack device.
    """

    def __init__(self, labjack: LabJackConnection):
        """
        Initializes a LoadCellSensor object.

        Args:
            labjack (LabJackConnection): An instance of LabJackConnection used for communication with the LabJack device.
        """
        self.loadcell = {
            "loadcell": LoadCell(
                LABJACK_PINS["load_cell"], LABJACK_PINS["d1_servo_feedback"]
            )
        }
        self.labjack = labjack

    def _get_loadcell(self, load_cell_name: str) -> LoadCell:
        """
        Retrieves a Load cell object based on the servo name.

        Args:
            load_cell_name (str): The name of the servo.

        Returns:
            Servo: The Servo object.

        Raises:
            ServoNotFoundError: If the servo with the specified name is not found.
        """
        if load_cell_name not in self.loadcell:
            logger.error("Servo not found")
            raise LoadCellError("Servo not found")
        return self.loadcell[load_cell_name]

    def get_loadcell_feedback(self, load_cell_name: str) -> float:
        """
        Retrieves the feedback value of a loadcell.

        Args:
            load_cell_name (str): The name of the servo.

        Returns:
            float: The feedback value of the servo.
        """
        servo = self._get_servo(load_cell_name)
        feedback_value = self.labjack.read(servo.feedback_pin)
        return feedback_value
