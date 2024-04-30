from dataclasses import dataclass
import logging
from app.hardware import LabJackConnection
from app.exceptions import ServoNotFoundError
from app.config import LABJACK_PINS

logger = logging.getLogger(__name__)


@dataclass
class Servo:
    input_pin: str
    feedback_pin: str


class ServoController:
    """
    A class that controls servos using a LabJackConnection.

    Attributes:
        servos (dict): A dictionary of servos with servo names as keys and Servo objects as values.
        labjack (LabJackConnection): An instance of LabJackConnection used for communication with the LabJack device.
    """

    def __init__(self, labjack: LabJackConnection):
        """
        Initializes a ServoController object.

        Args:
            labjack (LabJackConnection): An instance of LabJackConnection used for communication with the LabJack device.
        """
        self.servos = {
            "d1_servo": Servo(LABJACK_PINS["d1_servo_pwm"], LABJACK_PINS["d1_servo_feedback"])}
        self.labjack = labjack

    def _get_servo(self, servo_name: str) -> Servo:
        """
        Retrieves a Servo object based on the servo name.

        Args:
            servo_name (str): The name of the servo.

        Returns:
            Servo: The Servo object.

        Raises:
            ServoNotFoundError: If the servo with the specified name is not found.
        """
        if servo_name not in self.servos:
            logger.error("Servo not found")
            raise ServoNotFoundError("Servo not found")
        return self.servos[servo_name]

    def actuate_servo(self, servo_name: str, duty_cycle: float) -> str:
        """
        Actuates a servo with the specified PWM value.

        Args:
            servo_name (str): The name of the servo.
            duty_cycle (float): The duty cycle to set for the servo.

        Returns:
            str: A message indicating that the servo has been actuated with the specified PWM value.
        """
        servo = self._get_servo(servo_name)
        self.labjack.servo_pwm_write(servo.input_pin, duty_cycle)
        return f"Servo {servo_name} actuated with PWM value {duty_cycle}"

    def get_servo_feedback(self, servo_name: str) -> float:
        """
        Retrieves the feedback value of a servo.

        Args:
            servo_name (str): The name of the servo.

        Returns:
            float: The feedback value of the servo.
        """
        servo = self._get_servo(servo_name)
        feedback_value = self.labjack.read(servo.feedback_pin)
        return feedback_value
