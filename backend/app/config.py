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
    "engine_input": ("FIO4", "FIO5"),
    "engine_output": ("MI01", "MIO2"),
    "relief_input": ("FIO2", "FIO3"),
    "relief_output": ("FIO6", "FIO7"),
    # "d1_servo_pwm": "FIO0",
    # "d1_servo_feedback": "AIN3",
    "pressure_transducer_supply": "AIN5", # supply
    "pressure_transducer_fill": "AIN4", # fill
    "pressure_transducer_tank": "AIN12",  # tank top
    "pressure_transducer_chamber": "AIN10",  # chamber
    "thermocouple_engine": "AIN2",

    "pilot_valve_motor_enable": "EIO3",
    "pilot_valve_motor_in_1": "EIO4",
    "pilot_valve_motor_in_2": "EIO5",
    "pilot_valve_limit_switch_base": "EIO0",
    "pilot_valve_limit_switch_work": "EIO1",

    "ignitor_relay_pin": "CIO1",
    "qd_relay_pin": "CIO2",
    "vent_relay_pin": "CIO3",

    "active_vent_servo_pwm": "DIO0",
    "active_vent_relay_pin": "CIO0",

    "load_cell": ("AIN8", "AIN9") 
    #AV servo pwm DIO0
}

