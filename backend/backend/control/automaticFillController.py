from backend.sensors.pressureTransducerMC import PressureTransducerMC
from backend.sensors.thermocoupleMC import ThermocoupleMC
# NEED TO IMPORT CAPACITIVE FILL SENSOR
from backend.actuators.activeVent import ActiveVent  # NEED TO GET AV FROM MC
from backend.actuators.hanbayValve import HanbayValve
from backend.util.constants import BinaryPosition
import logging
import asyncio
from enum import Enum

class StateInfo:
    def __init__(self, cooldown, last_actuation_time=0):
        self.cooldown = cooldown
        self.last_actuation_time = last_actuation_time

class AutomaticFillController:
    """
    AutomaticFillController manages the automated process of filling and venting a tank based on mass and temperature conditions.

    Attributes:
        cap_fill: A CapacitiveFillSensor instance to measure tank mass.
        tank_tc: A ThermocoupleMC instance to measure tank temperature.
        active_vent: An ActiveVent instance to control the tank's vent.
        fill_valve: A HanbayValve instance to control the tank's fill valve.
        err_temp: Temperature tolerance as a factor (e.g., 1.03 means 3% above/below target).
        err_mass: Mass tolerance as a factor (e.g., 1.03 means 3% above/below target).
        event_array: A list to log events during operation.
        fill_freq: Minimum wait time (in seconds) between consecutive fill valve actuations.
        vent_freq: Minimum wait time (in seconds) between consecutive vent valve actuations.
        state: Current operational state of the system (STEADY, FILLING, or VENTING).
        last_actuation_time: A dictionary to track the last actuation timestamp for each state.
    """
    class State(Enum):
        """Enumeration for system states."""
        STEADY = "steady"
        VENTING = "venting"
        FILLING = "filling"
        HEATING = "heating"

    def __init__(self, cap_fill, tank_tc: ThermocoupleMC, active_vent: ActiveVent, fill_valve: HanbayValve):
        """
        Initializes the AutomaticFillController with sensors, actuators, and default tolerances.

        Args:
            tank_pt: Pressure transducer sensor for mass measurement.
            tank_tc: Thermocouple sensor for temperature measurement.
            active_vent: ActiveVent actuator to vent the tank.
            fill_valve: HanbayValve actuator to fill the tank.
        """
        self.logger = logging.getLogger(__name__)

        self.cap_fill = cap_fill
        self.tank_tc = tank_tc
        self.active_vent = active_vent
        self.fill_valve = fill_valve

        self.err_temp = 0.03
        self.err_mass = 0.03

        self.state_info = {
            self.State.FILLING: StateInfo(cooldown=5),
            self.State.VENTING: StateInfo(cooldown=5),
            self.State.STEADY: StateInfo(cooldown=5),
            self.State.HEATING: StateInfo(cooldown=5)
        }

        self.state = self.State.VENTING  # Initial state

    def try_transition(self, new_state):
        """
        Attempts to transition to a new state based on the cooldown period.

        Args:
            new_state: The state to transition to.

        Returns:
            The new state if the transition is allowed, otherwise the current state.
        """
        current_time = asyncio.get_event_loop().time()
        state_info = self.state_info[new_state]
        if current_time - state_info.last_actuation_time >= state_info.cooldown:
            state_info.last_actuation_time = current_time
            self.logger.info(f"Transitioned from state: {self.state} to state: {new_state}")
            return new_state
        self.logger.info(f"Failed transitioning to state: {new_state} to state: {self.state}. Can transition after {state_info.cooldown - (current_time - state_info.last_actuation_time)} seconds.")
        return self.state

    async def target_fill(self, fill_temp, targ_ox_mass):
        """
        Main control loop to manage the filling process based on target temperature and mass.

        Args:
            fill_temp: Target temperature in Celsius.
            targ_ox_mass: Target mass.
        """
        fill_temp += 273.15  # Convert to Kelvin

        err_temp_actual = self.err_temp / 3
        err_mass_actual = self.err_mass / 3

        while True:
            current_temp = await self.tank_tc.read()
            current_mass = await self.cap_fill.get_mass()

            self.update_state(current_temp, current_mass, fill_temp, targ_ox_mass, err_temp_actual, err_mass_actual)
            await self.apply_state()

            await asyncio.sleep(1)

    def update_state(self, current_temp, current_mass, target_fill_temp, target_ox_mass, error_temp, error_mass):
        """
        Updates the system's state based on current conditions and tolerances.

        Logic:
            - Transitions to FILLING if mass is below the lower error margin.
            - Transitions to VENTING if mass exceeds the upper error margin or the temperature exceeds the upper error margin.
            - Transitions to HEATING if temperature is below the lower error margin.
            - Transitions to STEADY if mass and temperature fall within acceptable ranges.

        Args:
            curr_temp: Current tank temperature in Kelvin.
            curr_mass: Current tank mass.
            fill_temp: Target temperature in Kelvin.
            targ_ox_mass: Target mass.
            err_temp: Error margin for temperature.
            err_mass: Error margin for mass.
        """
        above_mass = current_mass > target_ox_mass * (1 + error_mass)
        below_mass = current_mass < target_ox_mass * (1 - error_mass)
        above_temp = current_temp > target_fill_temp * (1 + error_temp)
        below_temp = current_temp < target_fill_temp * (1 - error_temp)

        if self.state == self.State.STEADY:
            if above_mass or above_temp:
                self.state = self.try_transition(self.State.VENTING)
            elif below_mass:
                self.state = self.try_transition(self.State.FILLING)
            elif below_temp:
                self.state = self.try_transition(self.State.HEATING)

        elif self.state == self.State.FILLING:
            if above_mass:
                self.state = self.try_transition(self.State.VENTING)
            elif not below_mass and not below_temp and not above_mass and not above_temp:
                self.state = self.try_transition(self.State.STEADY)

        elif self.state == self.State.VENTING:
            if below_mass:
                self.state = self.try_transition(self.State.FILLING)
            if below_temp:
                self.state = self.try_transition(self.State.HEATING)
            elif not below_mass and not below_temp and not above_mass and not above_temp:
                self.state = self.try_transition(self.State.STEADY)
        
        elif self.state == self.State.HEATING:
            if above_mass or above_temp:
                self.state = self.try_transition(self.State.VENTING)
            elif below_mass:
                self.state = self.try_transition(self.State.FILLING)
            elif not below_mass and not below_temp and not above_mass and not above_temp:
                self.state = self.try_transition(self.State.STEADY)

    async def apply_state(self):
        """
        Executes actions based on the current state by actuating the appropriate valves.

        This method translates the current state into specific actuator commands.
        """
        if self.state == self.State.FILLING:
            await self.active_vent.move_to_close()
            await self.fill_valve.actuate_valve(BinaryPosition.OPEN)

        elif self.state == self.State.VENTING:
            await self.active_vent.move_to_open()
            await self.fill_valve.actuate_valve(BinaryPosition.CLOSE)

        elif self.state == self.State.STEADY:
            await self.active_vent.move_to_close()
            await self.fill_valve.actuate_valve(BinaryPosition.CLOSE)

        elif self.state == self.State.HEATING:
            await self.active_vent.move_to_close()
            await self.fill_valve.actuate_valve(BinaryPosition.CLOSE)
