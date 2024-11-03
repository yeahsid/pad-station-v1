from backend.actuators.abstractActuator import AbstractActuator
from backend.actuators.pilotValve import PilotValve
from backend.actuators.activeVent import ActiveVent
from backend.actuators.hanbayValve import HanbayValve
from backend.actuators.relay import Relay
from backend.sensors.abstractSensors import AbstractAnalogSensor, AbstractDigitalSensor
from backend.sensors.hanbayValveFeedbackSensor import HanbayValveFeedbackSensor
from backend.sensors.dcMotorLimitSwitchSensor import DcMotorLimitSwitchSensor
from backend.sensors.pressureTransducer import PressureTransducer
from backend.sensors.loadCell import LoadCell
from backend.sensors.thermocouple import Thermocouple
from backend.control.labjack import LabJack
from backend.control.streamingLoggingController import StreamingLoggingController
from backend.config import *
from backend.util.constants import BinaryPosition
import asyncio
import logging



class PadStationController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.labjack = LabJack()
        self.digital_sensors: dict[str, AbstractDigitalSensor] = self._initialize_digital_sensors()
        self.analog_sensors: dict[str, AbstractAnalogSensor] = self._initialize_analog_sensors()
        self.actuators: dict[str, AbstractActuator] = self._initialize_actuators()
        self.streaming_controller = StreamingLoggingController(self.actuators, self.analog_sensors, self.digital_sensors)

    def _initialize_digital_sensors(self):
        return {
            LabJackPeripherals.FILL_VALVE.value: HanbayValveFeedbackSensor(
                LabJackPeripherals.FILL_VALVE.value, 
                LabJackPeripherals.FILL_VALVE_OUTPUT_PINS.value
            ),
            LabJackPeripherals.DUMP_VALVE.value: HanbayValveFeedbackSensor(
                LabJackPeripherals.DUMP_VALVE.value, 
                LabJackPeripherals.DUMP_VALVE_OUTPUT_PINS.value
            ),
            LabJackPeripherals.PILOT_VALVE.value: DcMotorLimitSwitchSensor(
                LabJackPeripherals.PILOT_VALVE.value, 
                LabJackPeripherals.PILOT_VALVE_LIMIT_SWITCH_TOP_PIN.value, 
                LabJackPeripherals.PILOT_VALVE_LIMIT_SWITCH_BOTTOM_PIN.value
            )
        }
    
    def _initialize_analog_sensors(self):
        sensors = {
            LabJackPeripherals.SUPPLY_PRESSURE_TRANSDUCER.value: PressureTransducer(
                LabJackPeripherals.SUPPLY_PRESSURE_TRANSDUCER.value, 
                LabJackPeripherals.SUPPLY_PRESSURE_TRANSDUCER_PIN.value
            ),
            LabJackPeripherals.FILL_PRESSURE_TRANSDUCER.value: PressureTransducer(
                LabJackPeripherals.FILL_PRESSURE_TRANSDUCER.value, 
                LabJackPeripherals.FILL_PRESSURE_TRANSDUCER_PIN.value
            ),
            LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_1.value: PressureTransducer(
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_1.value, 
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_1_PIN.value
            ),
            LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_2.value: PressureTransducer(
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_2.value, 
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_2_PIN.value
            ),
            LabJackPeripherals.LOAD_CELL.value: LoadCell(
                LabJackPeripherals.LOAD_CELL.value, 
                LabJackPeripherals.LOAD_CELL_PINS.value[0], 
                LabJackPeripherals.LOAD_CELL_PINS.value[1]
            ),
            LabJackPeripherals.THERMOCOUPLE.value: Thermocouple(
                LabJackPeripherals.THERMOCOUPLE.value, 
                LabJackPeripherals.THERMOCOUPLE_PIN.value
            )
        }
        return sensors
    
    def _initialize_actuators(self):
        relays = {
            LabJackPeripherals.IGNITOR_RELAY.value: Relay(LabJackPeripherals.IGNITOR_RELAY.value, LabJackPeripherals.IGNITOR_RELAY_PIN.value),
            LabJackPeripherals.ACTIVE_VENT_RELAY.value: Relay(LabJackPeripherals.ACTIVE_VENT_RELAY.value, LabJackPeripherals.ACTIVE_VENT_RELAY_PIN.value),
            LabJackPeripherals.QD_RELAY.value: Relay(LabJackPeripherals.QD_RELAY.value, LabJackPeripherals.QD_RELAY_PIN.value),
            LabJackPeripherals.EXTRA_RELAY.value: Relay(LabJackPeripherals.EXTRA_RELAY.value, LabJackPeripherals.EXTRA_RELAY_PIN.value)
        }
        valves = {
            LabJackPeripherals.FILL_VALVE.value: HanbayValve(
                LabJackPeripherals.FILL_VALVE.value,
                LabJackPeripherals.FILL_VALVE_INPUT_PINS.value,
                LabJackPeripherals.FILL_VALVE_OUTPUT_PINS.value,
                is_high_high_open=False,
                safe_position=BinaryPosition.CLOSE,
                output_state_sensor=self.digital_sensors[LabJackPeripherals.FILL_VALVE.value]
            ),
            LabJackPeripherals.DUMP_VALVE.value: HanbayValve(
                LabJackPeripherals.DUMP_VALVE.value,
                LabJackPeripherals.DUMP_VALVE_INPUT_PINS.value,
                LabJackPeripherals.DUMP_VALVE_OUTPUT_PINS.value,
                is_high_high_open=True,
                safe_position=BinaryPosition.OPEN,
                output_state_sensor=self.digital_sensors[LabJackPeripherals.DUMP_VALVE.value]
            ),
            LabJackPeripherals.PILOT_VALVE.value: PilotValve(
                LabJackPeripherals.PILOT_VALVE.value,
                LabJackPeripherals.PILOT_VALVE_MOTOR_ENABLE_PIN.value,
                LabJackPeripherals.PILOT_VALVE_MOTOR_IN_PINS.value,
                LabJackPeripherals.PILOT_VALVE_LIMIT_SWITCH_TOP_PIN.value,
                LabJackPeripherals.PILOT_VALVE_LIMIT_SWITCH_BOTTOM_PIN.value,
                safe_position=BinaryPosition.CLOSE,
                ignitor_relay=relays[LabJackPeripherals.IGNITOR_RELAY.value]
            ),
            LabJackPeripherals.ACTIVE_VENT.value: ActiveVent(
                LabJackPeripherals.ACTIVE_VENT.value,
                LabJackPeripherals.ACTIVE_VENT_SERVO_PWM.value,
                default_position=ACTIVE_VENT_CLOSED_POSITION,
                safe_position=ACTIVE_VENT_CLOSED_POSITION,
                power_relay=relays[LabJackPeripherals.ACTIVE_VENT_RELAY.value]
            )
        }
        return {**relays, **valves}

    async def start_streaming(self):
        await self.streaming_controller.start_streaming()

    async def stop_streaming(self):
        await self.streaming_controller.stop_streaming()

    async def gather_and_compile_data_frontend(self):
        # Compile data from sensors and actuators
        compiled_data = {}
        for sensor in self.analog_sensors.values():
            compiled_data[sensor.name] = await sensor.read()
        for sensor in self.digital_sensors.values():
            compiled_data[sensor.name] = (await sensor.read()).name

    async def _send_to_frontend(self, data):
        # Send data to the frontend at FRONTEND_UPDATE_RATE
        pass
        