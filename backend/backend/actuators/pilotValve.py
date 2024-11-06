import logging
from backend.actuators.dcMotor import DcMotor
from backend.util.constants import BinaryPosition
from backend.actuators.relay import Relay
import asyncio
from backend.util.config import PILOT_VALVE_TIMEOUT
from backend.sensors.dcMotorLimitSwitchSensor import DcMotorLimitSwitchSensor

class PilotValve(DcMotor):
    """
    Represents a pilot valve controlled by a DC motor and an ignitor relay.
    
    Attributes:
        ignitor_relay (Relay): Relay used for ignition sequence.
        armed (bool): Flag indicating if the ignition sequence is armed.
    """

    def __init__(self, name: str, motor_enable_pin: str, motor_in_pins: tuple[str, str], 
                 limit_switch_open_pin: str, limit_switch_close_pin: str, safe_position: BinaryPosition,
                 ignitor_relay: Relay, limit_switch_sensor: DcMotorLimitSwitchSensor):
        """
        Initializes the PilotValve with necessary pins and sensors.
        
        Args:
            name (str): Name of the pilot valve.
            motor_enable_pin (str): Pin to enable the motor.
            motor_in_pins (tuple[str, str]): Pins to control motor direction.
            limit_switch_open_pin (str): Pin for the open limit switch.
            limit_switch_close_pin (str): Pin for the close limit switch.
            safe_position (BinaryPosition): Safe position of the valve.
            ignitor_relay (Relay): Relay for ignition control.
            limit_switch_sensor (DcMotorLimitSwitchSensor): Sensor for limit switch feedback.
        """
        self.ignitor_relay = ignitor_relay
        self.armed = False

        super().__init__(
            name=name,
            motor_enable_pin=motor_enable_pin,
            motor_in_pins=motor_in_pins,
            limit_switch_open_pin=limit_switch_open_pin,
            limit_switch_close_pin=limit_switch_close_pin,
            limit_switch_sensor=limit_switch_sensor,
            safe_position=safe_position
        )
        
    logger = logging.getLogger(__name__)

    async def setup(self):
        """
        Sets up the pilot valve by invoking the DC motor setup.
        """
        await super().setup()

    async def actuate_valve(self, position: BinaryPosition):
        """
        Moves the valve to a specified binary position.
        
        Args:
            position (BinaryPosition): Desired position (OPEN or CLOSE).
        """
        await self.move_motor_to_position(position, PILOT_VALVE_TIMEOUT)
        
    async def arm(self):
        """
        Arms the ignition sequence, allowing it to be triggered.
        """
        self.armed = True
        self.logger.info("Ignition sequence armed")

    async def disarm(self):
        """
        Disarms the ignition sequence, preventing it from being triggered.
        """
        self.armed = False
        self.logger.info("Ignition sequence disarmed")

    async def ignition_sequence(self):
        """
        Executes the ignition sequence if armed.
        Fires the relay, moves the motor to OPEN, and resets the relay.
        """
        if not self.armed:
            self.logger.error("Ignition sequence not armed")
            return
        self.logger.info("Initiating ignition sequence")
        await self.ignitor_relay.fire()
        await self.move_motor_to_position(BinaryPosition.OPEN, PILOT_VALVE_TIMEOUT)
        await self.ignitor_relay.reset()
        self.armed = False
        self.logger.info("Ignition sequence complete")

    async def abort_ignition_sequence(self):
        """
        Aborts the ongoing ignition sequence by resetting the relay and moving the motor to CLOSE.
        """
        self.logger.info("Aborting ignition sequence")
        await self.ignitor_relay.reset()
        await self.move_motor_to_position(BinaryPosition.CLOSE, PILOT_VALVE_TIMEOUT)
        self.armed = False
        self.logger.info("Ignition sequence aborted")
