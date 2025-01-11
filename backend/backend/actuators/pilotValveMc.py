from backend.actuators.dcMotorMC import DcMotor
from backend.actuators.relay import Relay
from backend.util.constants import BinaryPosition

class PilotValve(DcMotor):
    def __init__(self, ignitor_relay: Relay, name: str, target_dev_id: int, target_act_id: int, safe_position: BinaryPosition):
        self.ignitor_relay = ignitor_relay
        self.armed = False

        super().__init__(
            name=name,
            target_dev_id=target_dev_id,
            target_act_id=target_act_id,
            safe_position=safe_position
        )
    
    def arm(self):
        self.armed = True
        self.logger.info("Ignition sequence armed")
    
    def disarm(self):
        self.armed = False
        self.logger.info("Ignition sequence disarmed")
    
    async def ignition_sequence(self):
        if not self.armed:
            self.logger.error("Ignition sequence not armed, aborting")
            return
    
        self.logger.info("Initiating ignition sequence")

        await self.ignitor_relay.fire()
        await self.spin_motor(BinaryPosition.OPEN)
        await self.ignitor_relay.reset()
        self.armed = False
    
        self.logger.info("Ignition sequence complete")
    
    async def abort_ignition_sequence(self):
        self.logger.info("Aborting ignition sequence")
        await self.ignitor_relay.reset()
        await self.spin_motor(BinaryPosition.CLOSE)
        self.armed = False
        self.logger.info("Ignition sequence aborted")

