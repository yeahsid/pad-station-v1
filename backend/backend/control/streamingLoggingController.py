from backend.actuators.abstractActuator import AbstractActuator
from backend.sensors.abstractSensors import AbstractAnalogSensor, AbstractDigitalSensor
from backend.control.labjack import LabJack
import asyncio
import numpy as np
import csv
from datetime import datetime

class StreamingLoggingController:

    def __init__(self, actuators: list[AbstractActuator], analog_sensors: list[AbstractAnalogSensor], digital_sensors: list[AbstractDigitalSensor]):
        self.labjack = LabJack()  # Access the singleton instance directly
        self.actuators = actuators
        self.analog_sensors = analog_sensors
        self.digital_sensors = digital_sensors

        self.streaming = False
        self.csv_file = None
        self.csv_writer = None
        self.event_csv_file = None
        self.event_csv_writer = None

        for actuator in self.actuators:
            actuator.register_event_handler(self.actuated_event_handler)

    async def actuated_event_handler(self, actuator: AbstractActuator, position):
        # Handle the event here
        # Insert the movement of the actuator into the logs here when the event is received
        # send the position of the actuator to the frontend
        event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.event_csv_writer.writerow([event_time, actuator.name, position])

    async def start_streaming(self):
        self.labjack.start_stream([sensor.streaming_address for sensor in self.analog_sensors])
        self.streaming = True
        header = ["time"] + [sensor.name for sensor in self.analog_sensors]
        converters = [lambda x: x] + [sensor.convert for sensor in self.analog_sensors]

        # Open the CSV file and write the header
        self.csv_file = open(f"streaming_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(header)

        # Open the event CSV file and write the header
        self.event_csv_file = open(f"event_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mode='w', newline='')
        self.event_csv_writer = csv.writer(self.event_csv_file)
        self.event_csv_writer.writerow(["time", "actuator", "position"])
        
        while self.streaming:
            data = self.labjack.read_stream()
            
            # Convert the data to the correct format using NumPy
            converted_data = np.empty_like(data, dtype=object)
            
            for i, converter in enumerate(converters):
                converted_data[:, i] = converter(data[:, i])
            
            # Write the converted data to the CSV file
            self.csv_writer.writerows(converted_data)
            
            # Send the last row of data (latest timestamp) to the frontend
            latest_data = converted_data[-1]
            print(f"Latest data: {latest_data}")  # Replace with actual logging and sending to frontend

            await asyncio.sleep(1 / self.labjack.real_scan_rate - 0.05)  # Adjust sleep time based on the scan rate

    async def stop_streaming(self):
        self.labjack.stop_stream()
        self.streaming = False
        if self.csv_file:
            self.csv_file.close()
        if self.event_csv_file:
            self.event_csv_file.close()