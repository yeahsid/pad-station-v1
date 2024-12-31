from backend.papiris import iris
from backend.papiris.iris.packet_types import *
from backend.papiris.hardware import IrisSerial

from backend.util.config import MotorControllerParams, MotorControllerPeripherals
from backend.sensors.pressureTransducerMC import PressureTransducerMC

import asyncio
import logging

class MotorController:
    def __init__(self, serial_interface: IrisSerial):
        self.logger = logging.getLogger(__name__)
        
        self.iris = iris.Iris(MotorControllerParams.SELF_DEV_ID.value, serial_interface)
        self.sensors = self._initialize_sensors()
    
    @classmethod
    async def get_connection(cls):
        serial_interface = await IrisSerial.get_connection(MotorControllerParams.SERIAL_COM_PORT.value, MotorControllerParams.SERIAL_BAUD_RATE.value)

        return cls(serial_interface)

    def _initialize_sensors(self):
        sensors = {
            MotorControllerPeripherals.PRESSURE_TRANSDUCER_1.value: PressureTransducerMC(
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1.value,
                self.iris,
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1_DEV_ID.value,
                MotorControllerPeripherals.PRESSURE_TRANSDUCER_1_PT_ID.value
            ),
            # MotorControllerPeripherals.PRESSURE_TRANSDUCER_2.value: PressureTransducerMC(
            #     MotorControllerPeripherals.PRESSURE_TRANSDUCER_2.value,
            #     self.iris,
            #     MotorControllerPeripherals.PRESSURE_TRANSDUCER_2_DEV_ID.value,
            #     MotorControllerPeripherals.PRESSURE_TRANSDUCER_2_PT_ID.value
            # )
        }

        return sensors

    async def gather_and_compile_data_frontend(self):
        compiled_data = {}
        for sensor in self.sensors.values():
            compiled_data[sensor.name] = await sensor.get_reading()

        return compiled_data
