from backend.papiris import iris
from backend.papiris.hardware import IrisSerial

from backend.util.config import MotorControllerParams, MotorControllerPeripherals, LabJackPeripherals
from backend.sensors.abstractSensors import AbstractAnalogSensor
from backend.sensors.pressureTransducerMC import PressureTransducerMC
from backend.sensors.thermocoupleMC import ThermocoupleMC
from backend.sensors.limitSwitchMC import LimitSwitch
from backend.sensors.dcMotorStateSensor import DcMotorStateSensor
from backend.control.abstractSystemController import AbstractSystemController
from backend.actuators.pilotValveMc import PilotValve
from backend.actuators.servoMC import ServoMotor
from backend.util.constants import BinaryPosition
from backend.control.padStationController import PadStationController

import asyncio
from datetime import datetime
import numpy as np

class MotorController(AbstractSystemController):
    def __init__(self, serial_interface: IrisSerial, pad_station: PadStationController):        
        self.iris = iris.Iris.create_instance(MotorControllerParams.SELF_DEV_ID.value, serial_interface)
        self.pad_station = pad_station

        super().__init__()
    
    @classmethod
    async def get_connection(cls, pad_station: PadStationController):
        serial_interface = await IrisSerial.get_connection(MotorControllerParams.SERIAL_COM_PORT.value, MotorControllerParams.SERIAL_BAUD_RATE.value)

        return cls(serial_interface, pad_station)

    def _initialize_analog_sensors(self):
        # pt and tc
        sensors = {
            MotorControllerPeripherals.PRESSURE_TRANSDUCER_1.value: PressureTransducerMC(
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1.value,
                None,
                True,
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1_DEV_ID.value,
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1_SENS_ID.value
            ),
            MotorControllerPeripherals.THERMOCOUPLE_1.value: ThermocoupleMC(
                MotorControllerPeripherals.THERMOCOUPLE_1.value,
                None,
                True,
                MotorControllerPeripherals.THERMOCOUPLE_1_DEV_ID.value,
                MotorControllerPeripherals.THERMOCOUPLE_1_SENS_ID.value
            )
        }

        return sensors

    def _initialize_digital_sensors(self):
        # limit switches will be in here
        pv_open_ls = LimitSwitch(
            MotorControllerPeripherals.PILOT_VALVE_OLS.value,
            MotorControllerPeripherals.PILOT_VALVE_DEV_ID.value,
            MotorControllerPeripherals.PILOT_VALVE_OLS_SENS_ID.value
        )
        pv_closed_ls = LimitSwitch(
            MotorControllerPeripherals.PILOT_VALVE_CLS.value,
            MotorControllerPeripherals.PILOT_VALVE_DEV_ID.value,
            MotorControllerPeripherals.PILOT_VALVE_CLS_SENS_ID.value
        )

        sensors = {
            MotorControllerPeripherals.PILOT_VALVE_SENS.value: DcMotorStateSensor(
                MotorControllerPeripherals.PILOT_VALVE_SENS.value,
                pv_open_ls,
                pv_closed_ls
            )
        }
        
        return sensors

    def _initialize_actuators(self):
        # pv and active vent
        actuators = {
            MotorControllerPeripherals.PILOT_VALVE.value: PilotValve(
                self.pad_station.actuators[LabJackPeripherals.IGNITOR_RELAY.value],
                MotorControllerPeripherals.PILOT_VALVE.value,
                MotorControllerPeripherals.PILOT_VALVE_DEV_ID.value,
                MotorControllerPeripherals.PILOT_VALVE_ACT_ID.value,
                BinaryPosition.CLOSE
            ),
            MotorControllerPeripherals.ACTIVE_VENT.value: ServoMotor(
                MotorControllerPeripherals.ACTIVE_VENT.value,
                MotorControllerPeripherals.ACTIVE_VENT_DEV_ID.value,
                MotorControllerPeripherals.ACTIVE_VENT_ACT_ID.value,
                MotorControllerPeripherals.ACTIVE_VENT_SAFE_PWM.value
            )
        }
        
        return actuators

    def start_sensor_streaming(self):
        streaming_sensors = []

        for sensor in self.analog_sensors.values():
            if sensor.streaming_enabled:
                sensor.set_streaming()
                streaming_sensors.append(sensor)
        
        asyncio.create_task(self._sensor_polling_task(streaming_sensors))

        return streaming_sensors, (1 / MotorControllerParams.SENSOR_POLL_RATE)
        
    async def _sensor_polling_task(sensors: list[AbstractAnalogSensor]):
        while True:
            for sensor in sensors:
                value = sensor.convert_single(await sensor.get_raw_value())
                sensor.set_streaming(value)
            
            await asyncio.sleep(1 / MotorControllerParams.SENSOR_POLL_RATE)

    def read_stream(self):
        data = [sensor.read_stored_value() for sensor in self.analog_sensors.values() if sensor.is_streaming]
        timestamp = datetime.now()

        array = np.array([[timestamp, *data]])

        return array

    def update_sensors_from_stream(self, data):
        pass

    def end_sensor_streaming(self):
        for sensor in self.analog_sensors.values():
            if sensor.is_streaming:
                sensor.deactivate_streaming()

    async def gather_and_compile_data_frontend(self):
        compiled_data = {}
        for sensor in self.analog_sensors.values():
            compiled_data[sensor.name] = await sensor.read()
        
        for sensor in self.digital_sensors.values():
            compiled_data[sensor.name] = (await sensor.read()).name  # name of the enum state it's in

        return compiled_data
