from dataclasses import dataclass
import logging
from backend.actuators.dcMotor import DcMotor
from backend.util.constants import BinaryPosition
from backend.actuators.relay import Relay
import asyncio
from backend.config import PILOT_VALVE_TIMEOUT


@dataclass
class PilotValve(DcMotor):
    ignitor_relay: Relay
    armed = False
    
    logger = logging.getLogger(__name__)

    async def actuate_valve(self, position: BinaryPosition):
        await self.move_motor_to_position(position, PILOT_VALVE_TIMEOUT)
        
    async def arm(self):
        self.armed = True
        self.logger.info("Ignition sequence armed")

    async def disarm(self):
        self.armed = False
        self.logger.info("Ignition sequence disarmed")

    async def ignition_sequence(self):
        if not self.armed:
            self.logger.error("Ignition sequence not armed")
            return
        self.logger.info("Initiating ignition sequence")
        await self.ignitor_relay.fire()
        await self.move_motor_to_position(BinaryPosition.OPEN, PILOT_VALVE_TIMEOUT)
        await self.ignitor_relay.reset()
        self.logger.info("Ignition sequence complete")

    async def abort_ignition_sequence(self):
        self.logger.info("Aborting ignition sequence")
        await asyncio.gather(
            self.ignitor_relay.reset(),
            await self.move_motor_to_position(BinaryPosition.CLOSE, PILOT_VALVE_TIMEOUT)
        )
        self.logger.info("Ignition sequence aborted")
