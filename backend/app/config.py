"""
This module defines the LabJack pin configuration for the pad station application.

The `LABJACK_PINS` dictionary maps pin names to their corresponding LabJack pin numbers.

Pin Configuration:
- `engine_input`: Pin numbers for engine input.
- `engine_output`: Pin numbers for engine output.
- `relief_input`: Pin numbers for relief input.
- `relief_output`: Pin numbers for relief output.
- `d1_servo_pwm`: Pin number for D1 servo PWM.
- `d1_servo_feedback`: Pin number for D1 servo feedback.
"""

LABJACK_PINS = {
    "engine_input": ("FIO3", "FIO2"),
    "engine_output": ("MIO1", "MIO0"),
    "relief_input": ("FIO7", "FIO6"),
    "relief_output": ("FIO5", "FIO4"),
    # "d1_servo_pwm": "FIO0",
    # "d1_servo_feedback": "AIN3",
    "pressure_transducer_supply": "AIN13", # supply
    "pressure_transducer_fill": "AIN2", # fill
    "pressure_transducer_tank": "AIN3",  # tank top
    "pressure_transducer_chamber": "AIN12",  # chamber
    "thermocouple_engine": "AIN0",

    "pilot_valve_motor_enable": "CIO3",
    "pilot_valve_motor_in_1": "CIO1",
    "pilot_valve_motor_in_2": "CIO0",
    "pilot_valve_limit_switch_base": "EIO7",
    "pilot_valve_limit_switch_work": "EIO6",

    "ignitor_relay_pin": "CIO2",
    "vent_relay_pin": "EIO2",
    "qd_relay_pin": "EIO3",

    "load_cell_test_stand": ("AIN8", "AIN9") 
}

