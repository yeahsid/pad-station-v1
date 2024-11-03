"""
This module defines the LabJack pin configuration for the pad station application.

The `LabJackPins` enum maps pin names to their corresponding LabJack pin numbers.

"""

from enum import Enum

FRONTEND_UPDATE_RATE = 1 # Hz
TARGET_SCAN_RATE = 10000 # Hz, stream scan rate
DIGITAL_SENSOR_UPDATE_RATE = 1 # Hz


ACTIVE_VENT_CLOSED_POSITION = 95000  # RICKY CHANGE THIS
ACTIVE_VENT_OPEN_POSITION = 111000  # RICKY CHANGE THIS

PILOT_VALVE_TIMEOUT = 50 # seconds

PRESSURE_TRANSDUCER_CALIBRATION = (0.0, 1.0)  # (offset, scale)
PRESSURE_TRANSDUCER_READ_VS = True 
# If True scales the pressure transducer readings to account for the Vs pin voltage variation
# If False assumes the Vs pin voltage is 4.7V
LOAD_CELL_CALIBRATION = (0.0, 1.0)  # (offset, scale)


class LabJackPeripherals(Enum):
    # Fill Box Valves
    FILL_VALVE = "Fill Valve"
    FILL_VALVE_INPUT_PINS = ("FIO4", "FIO5")
    FILL_VALVE_OUTPUT_PINS = ("MI01", "MIO2")
    DUMP_VALVE = "Dump Valve"
    DUMP_VALVE_INPUT_PINS = ("FIO2", "FIO3")
    DUMP_VALVE_OUTPUT_PINS = ("FIO6", "FIO7")
    

    # Pilot Valve
    PILOT_VALVE = "Pilot Valve"
    PILOT_VALVE_MOTOR_ENABLE_PIN = "EIO3"
    PILOT_VALVE_MOTOR_IN_1_PIN = "EIO4"
    PILOT_VALVE_MOTOR_IN_2_PIN = "EIO5"
    PILOT_VALVE_LIMIT_SWITCH_TOP_PIN = "EIO0"
    PILOT_VALVE_LIMIT_SWITCH_BOTTOM_PIN = "EIO1"

    # Active Vent
    ACTIVE_VENT = "Active Vent"
    ACTIVE_VENT_SERVO_PWM = "DIO0"
    ACTIVE_VENT_RELAY_PIN = "CIO0"

    # Pyro Channels
    IGNITOR_RELAY = "Ignitor Relay"
    IGNITOR_RELAY_PIN = "CIO1"
    QD_RELAY = "QD Relay"
    QD_RELAY_PIN = "CIO2"
    EXTRA_RELAY = "Extra Relay"
    EXTRA_RELAY_PIN = "CIO3"

    # Fill Box PTs
    SUPPLY_PRESSURE_TRANSDUCER = "Supply Pressure Transducer"
    SUPPLY_PRESSURE_TRANSDUCER_PIN = "AIN5"
    FILL_PRESSURE_TRANSDUCER = "Fill Pressure Transducer"
    FILL_PRESSURE_TRANSDUCER_PIN = "AIN4"
    PRESSURE_TRANSDUCER_Vs_PIN = "AIN13" # THIS IS NOT PLUGGED IN

    # External Sensors
    EXTERNAL_PRESSURE_TRANSDUCER_1 = "External Pressure Transducer 1"
    EXTERNAL_PRESSURE_TRANSDUCER_1_PIN = "AIN12"
    EXTERNAL_PRESSURE_TRANSDUCER_2 = "External Pressure Transducer 2"
    EXTERNAL_PRESSURE_TRANSDUCER_2_PIN = "AIN10"
    THERMOCOUPLE = "Thermocouple"
    THERMOCOUPLE_PIN = "AIN2"
    LOAD_CELL = "Load Cell"
    LOAD_CELL_PINS = ("AIN8", "AIN9")