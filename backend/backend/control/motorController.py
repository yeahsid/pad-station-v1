from backend.papiris import iris
from backend.papiris.hardware import IrisSerial

from backend.util.config import MotorControllerParams, MotorControllerPeripherals
from backend.sensors.abstractSensors import AbstractAnalogSensor
from backend.sensors.pressureTransducerMC import PressureTransducerMC
from backend.sensors.thermocoupleMC import ThermocoupleMC
from backend.control.abstractSystemController import AbstractSystemController
from backend.control.newStreamingLoggingController import StreamingLoggingController
from backend.actuators.dcMotorMC import DcMotor
from backend.util.constants import BinaryPosition

import asyncio
import logging
from datetime import datetime
import numpy as np

class MotorController(AbstractSystemController):
    def __init__(self, serial_interface: IrisSerial):        
        self.iris = iris.Iris.create_instance(MotorControllerParams.SELF_DEV_ID.value, serial_interface)

        super().__init__()
    
    @classmethod
    async def get_connection(cls):
        serial_interface = await IrisSerial.get_connection(MotorControllerParams.SERIAL_COM_PORT.value, MotorControllerParams.SERIAL_BAUD_RATE.value)

        return cls(serial_interface)

    def _initialize_analog_sensors(self):
        # pt and tc
        sensors = {
            MotorControllerPeripherals.PRESSURE_TRANSDUCER_1.value: PressureTransducerMC(
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1.value,
                None,
                self.iris,
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1_DEV_ID.value,
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1_SENS_ID.value
            ),
            MotorControllerPeripherals.THERMOCOUPLE_1.value: ThermocoupleMC(
                MotorControllerPeripherals.THERMOCOUPLE_1.value,
                None,
                self.iris,
                MotorControllerPeripherals.THERMOCOUPLE_1_DEV_ID.value,
                MotorControllerPeripherals.THERMOCOUPLE_1_SENS_ID.value
            )
        }

        return sensors

    def _initialize_digital_sensors(self):
        # limit switches will be in here
        pass

    def _initialize_actuators(self):
        # pv and active vent
        actuators = {
            MotorControllerPeripherals.PILOT_VALVE.value: DcMotor(
                MotorControllerPeripherals.PILOT_VALVE.value,
                MotorControllerPeripherals.PILOT_VALVE_DEV_ID.value,
                MotorControllerPeripherals.PILOT_VALVE_ACT_ID.value,
                BinaryPosition.CLOSE
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
        data = [sensor.read() for sensor in self.analog_sensors.values() if sensor.is_streaming]
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

        return compiled_data

# class MotorController:
#     def __init__(self, serial_interface: IrisSerial):
#         self.logger = logging.getLogger(__name__)
        
#         self.iris = iris.Iris.create_instance(MotorControllerParams.SELF_DEV_ID.value, serial_interface)
#         self.sensors = self._initialize_sensors()
    
#     @classmethod
#     async def get_connection(cls):
#         serial_interface = await IrisSerial.get_connection(MotorControllerParams.SERIAL_COM_PORT.value, MotorControllerParams.SERIAL_BAUD_RATE.value)

#         return cls(serial_interface)

#     def _initialize_sensors(self):
#         sensors = {
#             MotorControllerPeripherals.PRESSURE_TRANSDUCER_1.value: PressureTransducerMC(
#                 MotorControllerPeripherals.PRESSURE_TRANSDUCER_1.value,
#                 self.iris,
#                 MotorControllerPeripherals.PRESSURE_TRANSDUCER_1_DEV_ID.value,
#                 MotorControllerPeripherals.PRESSURE_TRANSDUCER_1_PT_ID.value
#             ),
#             # MotorControllerPeripherals.PRESSURE_TRANSDUCER_2.value: PressureTransducerMC(
#             #     MotorControllerPeripherals.PRESSURE_TRANSDUCER_2.value,
#             #     self.iris,
#             #     MotorControllerPeripherals.PRESSURE_TRANSDUCER_2_DEV_ID.value,
#             #     MotorControllerPeripherals.PRESSURE_TRANSDUCER_2_PT_ID.value
#             # )
#         }

#         return sensors

#     async def gather_and_compile_data_frontend(self):
#         compiled_data = {}
#         for sensor in self.sensors.values():
#             compiled_data[sensor.name] = await sensor.get_reading()

#         return compiled_data
