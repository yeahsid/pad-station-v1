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
from backend.sensors.capFill import CapFill

from backend.papiris.iris import SET_LOGGING_RequestStruct, SET_LOGGING_ResponseStruct, SET_TIME_MessageStruct, IrisPacketPriority, IRIS_ERR_TIMEOUT
from backend.papiris.iris import IrisPacket

import asyncio
from datetime import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor

SELF_DEV_ID = 0x0
TOP_BOARD_DEV_ID = 0x2
BOTTOM_BOARD_DEV_ID = 0x3
CAP_FILL_DEV_ID = 0x4

class MotorController(AbstractSystemController):
    def __init__(self, serial_interface: IrisSerial, pad_station: PadStationController):        
        self.iris: iris.Iris = iris.Iris.create_instance(MotorControllerParams.SELF_DEV_ID.value, serial_interface)
        self.pad_station = pad_station
        #self.executor = ThreadPoolExecutor(max_workers=1)

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
            ),
            MotorControllerPeripherals.CAP_FILL.value: CapFill(
                MotorControllerPeripherals.CAP_FILL.value,
                None,
                True,
                "I straight up don't care",
                "Yep"
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
            # MotorControllerPeripherals.PILOT_VALVE.value: PilotValve(
            #     self.pad_station.actuators[LabJackPeripherals.IGNITOR_RELAY.value],
            #     MotorControllerPeripherals.PILOT_VALVE.value,
            #     MotorControllerPeripherals.PILOT_VALVE_DEV_ID.value,
            #     MotorControllerPeripherals.PILOT_VALVE_ACT_ID.value,
            #     BinaryPosition.CLOSE
            # ),
            MotorControllerPeripherals.ACTIVE_VENT.value: ServoMotor(
                MotorControllerPeripherals.ACTIVE_VENT.value,
                MotorControllerPeripherals.ACTIVE_VENT_DEV_ID.value,
                MotorControllerPeripherals.ACTIVE_VENT_ACT_ID.value,
                MotorControllerPeripherals.ACTIVE_VENT_SAFE_PWM.value
            )
        }
        
        return actuators

    async def start_sensor_streaming(self):
        await self._start_motor_controller_streaming()

        self.streaming_sensors = []

        for sensor in self.analog_sensors.values():
            if sensor.streaming_enabled:
                sensor.set_streaming()
                self.streaming_sensors.append(sensor)

        asyncio.create_task(self._sensor_polling_task(self.streaming_sensors))

        return 1 / MotorControllerParams.SENSOR_POLL_RATE.value
    
    async def _start_motor_controller_streaming(self):
        # Tare time
        now = datetime.now()
        set_time_struct = SET_TIME_MessageStruct()
        set_time_struct.hour = now.hour
        set_time_struct.minute = now.minute
        set_time_struct.second = now.second
        set_time_struct.milisecond = now.microsecond // 1000

        await self.iris.send_message(IrisPacket.create_from_struct(
            IrisPacketPriority.IRIS_PACKET_PRIORITY_MEDIUM,
            set_time_struct,
            SELF_DEV_ID,
            3,  # mega scuffed, fix later, not used
            0
        ))

        # Start logging on top and bottom board
        start_logging_struct = SET_LOGGING_RequestStruct()
        start_logging_struct.logging_state = 0x1

        response_struct: SET_LOGGING_ResponseStruct
        for devid in (TOP_BOARD_DEV_ID, BOTTOM_BOARD_DEV_ID, CAP_FILL_DEV_ID):
            while True:  # loop until the fellas start logging
                try:
                    _, response_struct = await self.iris.send_request(
                        start_logging_struct,
                        priority=IrisPacketPriority.IRIS_PACKET_PRIORITY_MEDIUM,
                        other_dev_id=devid,
                        response_timeout=0.5
                    )
                except IRIS_ERR_TIMEOUT:
                    print(f"Set logging request to id '{devid}' timed out")
                else:
                    if response_struct.state == 0x1:
                        break

    async def _sensor_polling_task(self, sensors: list[AbstractAnalogSensor]):
        while True:
            for sensor in sensors:
                value = sensor.convert_single(await sensor.get_raw_value())
                sensor.set_streaming(value)
            
            await asyncio.sleep(1 / MotorControllerParams.SENSOR_POLL_RATE.value)

    def read_stream(self):
        data = [sensor.read_stored_value() for sensor in self.analog_sensors.values() if sensor.is_streaming]
        timestamp = datetime.now()

        array = np.array([[timestamp, *data]])

        return array

    def update_sensors_from_stream(self, data):
        pass

    async def end_sensor_streaming(self):
        # Stop logging on top and bottom board
        start_logging_struct = SET_LOGGING_RequestStruct()
        start_logging_struct.logging_state = 0x0

        response_struct: SET_LOGGING_ResponseStruct
        for devid in (TOP_BOARD_DEV_ID, BOTTOM_BOARD_DEV_ID, CAP_FILL_DEV_ID):
            while True:  # loop until the fellas start logging
                _, response_struct = await self.iris.send_request(
                    start_logging_struct,
                    priority=IrisPacketPriority.IRIS_PACKET_PRIORITY_MEDIUM,
                    other_dev_id=devid,
                    response_timeout=0.5
                )

                if response_struct.state == 0x1:
                    break

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
