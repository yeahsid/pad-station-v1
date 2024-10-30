"""
This module defines the LabJack pin configuration for the pad station application.

The `LABJACK_PINS` dictionary maps pin names to their corresponding LabJack pin numbers.

"""

LABJACK_PINS = {

    # Fill Box Valves
    "fill_valve_input": ("FIO4", "FIO5"), # In 0, In 1
    "fill_valve_output": ("MI01", "MIO2"), # Out 0, Out 1
    "dump_valve_input": ("FIO2", "FIO3"), # In 0, In 1
    "dump_valve_output": ("FIO6", "FIO7"), # Out 0, Out 1

    # Pilot Valve
    "pilot_valve_motor_enable": "EIO3", 
    "pilot_valve_motor_in_1": "EIO4", 
    "pilot_valve_motor_in_2": "EIO5",
    "pilot_valve_limit_switch_top": "EIO0",
    "pilot_valve_limit_switch_bottom": "EIO1",
    
    # Active Vent 
    "active_vent_servo_pwm": "DIO0",
    "active_vent_relay_pin": "CIO0",

    # Pyro Channels
    "ignitor_relay_pin": "CIO1",
    "qd_relay_pin": "CIO2",
    "vent_relay_pin": "CIO3",

    # Fill Box PTs
    "pressure_transducer_supply": "AIN5",
    "pressure_transducer_fill": "AIN4",

    # External Sensors
    "pressure_transducer_external_1": "AIN12",
    "pressure_transducer_external_2": "AIN10",
    "thermocouple": "AIN2",
    "load_cell": ("AIN8", "AIN9") , # Sig +, Sig -
}

