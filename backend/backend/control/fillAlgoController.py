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
from backend.control.padStationController import PadStationController
import asyncio
import logging
import time

class fillAlgoController:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.labjack = LabJack()
        self.digital_sensors: dict[str, AbstractDigitalSensor] = self._initialize_digital_sensors()
        self.analog_sensors: dict[str, AbstractAnalogSensor] = self._initialize_analog_sensors()
        self.actuators: dict[str, AbstractActuator] = self._initialize_actuators()
        self.actuated_event = asyncio.Event()
        self.streaming_controller = StreamingLoggingController(self.actuators.values(), self.analog_sensors.values(), self.digital_sensors.values(), self.actuated_event)

        self.err_temp = 1.03
        self.err_mass = 1.03
        self.event_array = []
        self.fill_freq = 5
        self.vent_freq = 5

        # Register event handlers for all actuators
        for actuator in self.actuators.values():
            actuator.register_event_handler(self.actuated_event_handler)

    async def set_temp_error(self, temp_error):
        self.err_temp = 1 + temp_error/100 

    async def set_mass_error(self, mass_error):
        self.err_mass = 1 + mass_error/100

    async def set_fill_freq(self, fill_freq):
        self.fill_freq = fill_freq

    async def set_vent_freq(self, vent_freq):
        self.vent_freq = vent_freq

    async def target_fill(self, fill_temp, targ_ox_mass, pad_station_controller):
        fill_temp = fill_temp + 273.15

        curr_temp = Thermocouple.get_raw_value()
        curr_mass = LoadCell.get_raw_value()

        venting = True #Tracks venting status
        filling = False #Tracks filling status
        steady = False #Tracks if the machine reaches steady state

        count = 0 #Used to track wait time between vent actuations
        count_f = 0 #Used to track wait time between fill actuations
        count_s = 0

        #Half the set error, used by algo to target middle of error range rather than staying on the edge of the thresholds
        err_temp_h = 1 + (self.err_temp-1)/3
        err_mass_h = 1 + (self.err_mass-1)/3

        count = count + 1
        count_f = count_f + 1
        if steady == True:
            count_s = count_s + 1

        if curr_mass <= targ_ox_mass*(2-err_mass_h) or (filling == True and count_f < self.fill_freq): #If the tank is below mass threshold or is already filling then fill
            if filling == False: #If it wasn't filling but now is reflect that in state and start counter for next actuation
                count_f = 0
            filling = True
        if curr_mass > targ_ox_mass*err_mass_h: #If the tank is above the mass threshold try to vent and stop filling
            if venting == False: #If it wasn't venting but now is reflect that in state and start counter for next actuation
                count = 0
            if filling == True and count_f >= self.fill_freq or filling == False: #Check if filling can be stopped is if it already is and then set states
                venting = True
                filling = False
                count_f = 0
        if curr_temp < fill_temp*(2-err_temp_h) or (venting == False and count < self.vent_freq): #If tank is too cold or vent is already closed and isn't allowed to actuate yet then hold closed
            if venting == True: #If it was venting but now isn't reflect that in state and start counter for next actuation
                count = 0
            venting = False
        if curr_temp > fill_temp*err_temp_h or (venting == True and count < self.vent_freq): #If tank is too hot or is already venting and isn't allowed to actuate yet then vent
            if venting == False: #If it wasn't venting but now is reflect that in state and start counter for next actuation
                count = 0
            venting = True
            
        elif curr_mass < targ_ox_mass*self.err_mass and curr_mass > targ_ox_mass*(2-self.err_mass) and curr_temp <= fill_temp*self.err_temp: #If tank is within all acceptable ranges update counters and read "steady"
            steady = True
            #If variables are steady then close vent and fill
            if venting == True:
                venting = False
                count = 0
            if filling == True:
                filling = False
                count_f = 0
        
            #Based on previous checks apply the following commands to the system
            if filling == True and venting == True: 
                self.event_array.append('too hot venting/filling')

                av: ActiveVent = pad_station_controller.actuators[LabJackPeripherals.ACTIVE_VENT.value]
                await av.move_to_open()

                fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
                await fv.actuate_valve(BinaryPosition.OPEN)
                
                
            elif venting == True and filling == False:
                self.event_array.append('too hot venting')

                av: ActiveVent = pad_station_controller.actuators[LabJackPeripherals.ACTIVE_VENT.value]
                await av.move_to_open()

                fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
                await fv.actuate_valve(BinaryPosition.CLOSE)
                
            elif venting == False and filling == True:
                self.event_array.append('too low filling')

                av: ActiveVent = pad_station_controller.actuators[LabJackPeripherals.ACTIVE_VENT.value]
                await av.move_to_close()

                fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
                await fv.actuate_valve(BinaryPosition.OPEN)

            elif steady == True:
                self.event_array.append('steady')

                av: ActiveVent = pad_station_controller.actuators[LabJackPeripherals.ACTIVE_VENT.value]
                await av.move_to_close()

                fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
                await fv.actuate_valve(BinaryPosition.CLOSE)
                
            elif venting == False and filling == False:
                self.event_array.append('heating')

                av: ActiveVent = pad_station_controller.actuators[LabJackPeripherals.ACTIVE_VENT.value]
                await av.move_to_close()

                fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
                await fv.actuate_valve(BinaryPosition.CLOSE)

