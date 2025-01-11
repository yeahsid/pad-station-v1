from backend.util.config import FRONTEND_UPDATE_RATE
from backend.actuators.abstractActuator import AbstractActuator
from backend.util.constants import BinaryPosition
from backend.papiris.iris import DCMOTOR_SPIN_RequestStruct, DCMOTOR_SPIN_ResponseStruct, IrisPacketPriority
from backend.papiris import iris


class DcMotor(AbstractActuator):
    """
    Represents a DC motor actuator with limit switch feedback.
    
    Attributes:
        name (str): Name of the motor.
        motor_enable_pin (str): Pin to enable the motor.
        motor_in_pins (tuple[str, str]): Pins to control motor direction.
        limit_switch_open_pin (str): Pin for the open limit switch.
        limit_switch_close_pin (str): Pin for the close limit switch.
        safe_position (BinaryPosition): Safe position of the motor.
        limit_switch_sensor (DcMotorLimitSwitchSensor): Sensor for limit switch feedback.
    """

    def __init__(self, name: str, target_dev_id: int, target_act_id: int, safe_position: BinaryPosition):
        self.iris = iris.Iris()
        self.target_dev_id = target_dev_id
        self.target_act_id = target_act_id
        self.safe_position = safe_position

        self.request_struct = DCMOTOR_SPIN_RequestStruct()
        self.request_struct.motor_select = self.target_act_id

        super().__init__(name)

    async def setup(self):
        """
        Sets up the DC motor. No additional setup required.
        """
        pass # No setup required for dc motor

    async def move_to_safe_position(self):
        """
        Moves the motor to its predefined safe position within a timeout.
        """
        await self.spin_motor(self.safe_position)
        self.logger.info(f"{self.name} motor moved to safe position")

    async def spin_motor(self, position: BinaryPosition):
        """
        Spins the motor to the specified binary position.
        
        Args:
            position (BinaryPosition): Desired position (OPEN or CLOSE).
        """

        self.request_struct.motor_state = 1 if position == BinaryPosition.OPEN else 0

        response_struct: DCMOTOR_SPIN_ResponseStruct
        _, response_struct = await self.iris.send_request(
            self.request_struct,
            IrisPacketPriority.IRIS_PACKET_PRIORITY_LOW,
            other_dev_id=self.target_dev_id,
            response_timeout=1 / FRONTEND_UPDATE_RATE
        )

        if response_struct.success:
            self.trigger_actuated_event(position)

        return response_struct.success
