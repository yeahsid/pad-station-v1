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
    "engine_input": ("FIO2", "FIO3"),
    "engine_output": ("FIO0", "FIO1"),
    "relief_input": ("FIO6", "FIO7"),
    "relief_output": ("FIO4", "FIO5"),
    "d1_servo_pwm": "FIO0",
    "d1_servo_feedback": "AIN3",
    "pressure_transducer_supply": "AIN13",
    "pressure_transducer_engine": "AIN12",
    "load_cell": ("AIN9", "AIN9")
}
