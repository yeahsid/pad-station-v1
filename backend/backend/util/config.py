"""
This module defines the LabJack pin configuration and calibration constants for the PadStation backend.
It includes enumerations for peripheral devices and their corresponding pin assignments.
"""

from enum import Enum

FRONTEND_UPDATE_RATE = 1  # Hz
TARGET_SCAN_RATE = 999    # Hz, stream scan rate
DIGITAL_SENSOR_UPDATE_RATE = 1  # Hz

ACTIVE_VENT_CLOSED_POSITION = 95000  # RICKY CHANGE THIS
ACTIVE_VENT_OPEN_POSITION = 111000   # RICKY CHANGE THIS

PILOT_VALVE_TIMEOUT = 50  # seconds

PRESSURE_TRANSDUCER_CALIBRATION = (-25.82, 54.87)  # (offset, scale)
PRESSURE_TRANSDUCER_READ_VS = False 
# If True scales the pressure transducer readings to account for the Vs pin voltage variation
# If False assumes the Vs pin voltage is 4.7V
LOAD_CELL_CALIBRATION = (0.0, 1.0)  # (offset, scale)

class LabJackPeripherals(Enum):
    """Enumeration of LabJack peripheral devices and their pin configurations."""
    # Fill Box Valves
    FILL_VALVE = "Fill Valve"
    FILL_VALVE_INPUT_PINS = ("FIO4", "FIO5")
    FILL_VALVE_OUTPUT_PINS = ("MIO1", "MIO2")
    DUMP_VALVE = "Dump Valve"
    DUMP_VALVE_INPUT_PINS = ("FIO2", "FIO3")
    DUMP_VALVE_OUTPUT_PINS = ("FIO6", "FIO7")
    
    # Pilot Valve
    PILOT_VALVE = "Pilot Valve"
    PILOT_VALVE_MOTOR_ENABLE_PIN = "EIO3"
    PILOT_VALVE_MOTOR_IN_PINS = ("EIO4", "EIO5")
    PILOT_VALVE_LIMIT_SWITCH_TOP_PIN = "EIO0"
    PILOT_VALVE_LIMIT_SWITCH_BOTTOM_PIN = "EIO1"

    # Active Vent
    ACTIVE_VENT = "Active Vent"
    ACTIVE_VENT_SERVO_PWM = "DIO0"
    ACTIVE_VENT_RELAY = "Active Vent Relay"
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
    SUPPLY_PRESSURE_TRANSDUCER_STREAMING_ENABLED = False
    FILL_PRESSURE_TRANSDUCER = "Fill Pressure Transducer"
    FILL_PRESSURE_TRANSDUCER_PIN = "AIN4"
    FILL_PRESSURE_TRANSDUCER_STREAMING_ENABLED = True
    PRESSURE_TRANSDUCER_Vs_PIN = "AIN13"  # THIS IS NOT PLUGGED IN

    # External Sensors
    EXTERNAL_PRESSURE_TRANSDUCER_1 = "External Pressure Transducer 1"
    EXTERNAL_PRESSURE_TRANSDUCER_1_PIN = "AIN12"
    EXTERNAL_PRESSURE_TRANSDUCER_1_STREAMING_ENABLED = False
    EXTERNAL_PRESSURE_TRANSDUCER_2 = "External Pressure Transducer 2"
    EXTERNAL_PRESSURE_TRANSDUCER_2_PIN = "AIN10"
    EXTERNAL_PRESSURE_TRANSDUCER_2_STREAMING_ENABLED = False
    THERMOCOUPLE = "Thermocouple"
    THERMOCOUPLE_PIN = "AIN2"
    THERMOCOUPLE_STREAMING_ENABLED = False  # Not possible to use EF functions when streaming
    LOAD_CELL = "Load Cell"
    LOAD_CELL_PINS = ("AIN8", "AIN9")
    LOAD_CELL_STREAMING_ENABLED = True

class MotorControllerParams(Enum):
    SERIAL_COM_PORT = "/dev/tty.usbserial-B001A43L"
    SERIAL_BAUD_RATE = 9600

    SELF_DEV_ID = 0x0
    TOP_BOARD_DEV_ID = 0x1
    BOTTOM_BOARD_DEV_ID = 0x2

    SENSOR_POLL_RATE = 3

class MotorControllerPeripherals(Enum):
    PRESSURE_TRANSDUCER_1 = "Tank Pressure Transducer"
    PRESSURE_TRANSDUCER_1_DEV_ID = 1
    PRESSURE_TRANSDUCER_1_SENS_ID = 0

    THERMOCOUPLE_1 = "Tank Temperature"
    THERMOCOUPLE_1_DEV_ID = 1
    THERMOCOUPLE_1_SENS_ID = 0

    PILOT_VALVE = "Pilot Valve"
    PILOT_VALVE_DEV_ID = 3
    PILOT_VALVE_ACT_ID = 0

    PILOT_VALVE_OLS = "Pilot Valve Open Limit Switch"
    PILOT_VALVE_OLS_SENS_ID = 0
    PILOT_VALVE_CLS = "Pilot Valve Closed Limit Switch"
    PILOT_VALVE_CLS_SENS_ID = 1
    PILOT_VALVE_SENS = "Pilot Valve State Sensor"

    ACTIVE_VENT = "Active Vent"
    ACTIVE_VENT_DEV_ID = 1
    ACTIVE_VENT_ACT_ID = 0
    ACTIVE_VENT_SAFE_PWM = 50
