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
from backend.util.config import *
from backend.util.constants import BinaryPosition
import asyncio
import logging
import time

class PadStationController:
    """
    Manages the overall operation of the Pad Station, including actuators and sensors.
    
    Attributes:
        logger (logging.Logger): Logger instance.
        labjack (LabJack): Singleton instance for LabJack device interaction.
        digital_sensors (dict[str, AbstractDigitalSensor]): Dictionary of digital sensors.
        analog_sensors (dict[str, AbstractAnalogSensor]): Dictionary of analog sensors.
        actuators (dict[str, AbstractActuator]): Dictionary of actuators.
        actuated_event (asyncio.Event): Event triggered when an actuator is actuated.
        streaming_controller (StreamingLoggingController): Controller for streaming and logging.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.labjack = LabJack()
        self.digital_sensors: dict[str, AbstractDigitalSensor] = self._initialize_digital_sensors()
        self.analog_sensors: dict[str, AbstractAnalogSensor] = self._initialize_analog_sensors()
        self.actuators: dict[str, AbstractActuator] = self._initialize_actuators()
        self.actuated_event = asyncio.Event()
        self.streaming_controller = StreamingLoggingController(self.actuators.values(), self.analog_sensors.values(), self.digital_sensors.values(), self.actuated_event)

        # Register event handlers for all actuators
        for actuator in self.actuators.values():
            actuator.register_event_handler(self.actuated_event_handler)

    async def actuated_event_handler(self, actuator: AbstractActuator, position):
        """
        Handles actuator events by writing them to the event CSV and setting the event.
        
        Args:
            actuator (AbstractActuator): The actuator that was actuated.
            position (int): The new position of the actuator.
        """
        self.streaming_controller.write_actuator_event_to_csv(actuator.name, position)
        self.actuated_event.set()

    def _initialize_digital_sensors(self):
        """
        Initializes all digital sensors used in the Pad Station.
        
        Returns:
            dict[str, AbstractDigitalSensor]: Dictionary of initialized digital sensors.
        """
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
        """
        Initializes all analog sensors used in the Pad Station.
        
        Returns:
            dict[str, AbstractAnalogSensor]: Dictionary of initialized analog sensors.
        """
        sensors = {
            LabJackPeripherals.SUPPLY_PRESSURE_TRANSDUCER.value: PressureTransducer(
                LabJackPeripherals.SUPPLY_PRESSURE_TRANSDUCER.value, 
                LabJackPeripherals.SUPPLY_PRESSURE_TRANSDUCER_PIN.value,
                LabJackPeripherals.SUPPLY_PRESSURE_TRANSDUCER_STREAMING_ENABLED.value
            ),
            LabJackPeripherals.FILL_PRESSURE_TRANSDUCER.value: PressureTransducer(
                LabJackPeripherals.FILL_PRESSURE_TRANSDUCER.value, 
                LabJackPeripherals.FILL_PRESSURE_TRANSDUCER_PIN.value,
                LabJackPeripherals.FILL_PRESSURE_TRANSDUCER_STREAMING_ENABLED.value
            ),
            LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_1.value: PressureTransducer(
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_1.value, 
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_1_PIN.value,
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_1_STREAMING_ENABLED.value
            ),
            LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_2.value: PressureTransducer(
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_2.value, 
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_2_PIN.value,
                LabJackPeripherals.EXTERNAL_PRESSURE_TRANSDUCER_2_STREAMING_ENABLED.value
            ),
            LabJackPeripherals.LOAD_CELL.value: LoadCell(
                LabJackPeripherals.LOAD_CELL.value, 
                LabJackPeripherals.LOAD_CELL_PINS.value[0], 
                LabJackPeripherals.LOAD_CELL_PINS.value[1],
                LabJackPeripherals.LOAD_CELL_STREAMING_ENABLED.value
            ),
            LabJackPeripherals.THERMOCOUPLE.value: Thermocouple(
                LabJackPeripherals.THERMOCOUPLE.value, 
                LabJackPeripherals.THERMOCOUPLE_PIN.value,
                LabJackPeripherals.THERMOCOUPLE_STREAMING_ENABLED.value
            )
        }
        return sensors
    
    def _initialize_actuators(self):
        """
        Initializes all actuators used in the Pad Station.
        
        Returns:
            dict[str, AbstractActuator]: Dictionary of initialized actuators.
        """
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
                limit_switch_sensor=self.digital_sensors[LabJackPeripherals.PILOT_VALVE.value],
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
        """
        Initiates the streaming of sensor data.
        """
        await self.streaming_controller.start_streaming()

    async def stop_streaming(self):
        """
        Stops the streaming of sensor data.
        """
        await self.streaming_controller.stop_streaming()

    async def gather_and_compile_data_frontend(self):
        """
        Gathers data from all sensors and compiles it for the frontend.
        
        Returns:
            dict: Compiled sensor data.
        """
        start = time.time()
        # Wait for the event or timeout
        waiting_actuated_event_time = time.time()
        try:
            start = time.time()
            await asyncio.wait_for(self.actuated_event.wait(), timeout=1 / FRONTEND_UPDATE_RATE)
            # waiting_actuated_event_time = time.time()
            # self.logger.debug(f"Waited for actuated event for {waiting_actuated_event_time - start} seconds")
        except asyncio.TimeoutError:
            pass
            # waiting_actuated_event_time = time.time()
            # self.logger.debug(f"Timeout for actuated event for {waiting_actuated_event_time - start} seconds")
        finally:
            self.actuated_event.clear()
            # clearing_actuated_event_time = time.time()
            # self.logger.debug(f"Clearing actuated event took {clearing_actuated_event_time - waiting_actuated_event_time} seconds")
        
        # Compile data from sensors and actuators
        compiled_data = {}
        for sensor in self.analog_sensors.values():
            compiled_data[sensor.name] = await sensor.read()
        # analog_sensor_time = time.time()
        # self.logger.debug(f"Reading analog sensors took {analog_sensor_time - waiting_actuated_event_time} seconds")

        for sensor in self.digital_sensors.values():
            compiled_data[sensor.name] = (await sensor.read()).name
        # digital_sensor_time = time.time()
        # self.logger.debug(f"Reading digital sensors took {digital_sensor_time - analog_sensor_time} seconds")
        return compiled_data