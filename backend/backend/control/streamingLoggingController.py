from backend.actuators.abstractActuator import AbstractActuator
from backend.sensors.abstractSensors import AbstractAnalogSensor, AbstractDigitalSensor
from backend.control.labjack import LabJack
import asyncio
import numpy as np
import csv
from datetime import datetime
import logging
import os

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

        self.logger = logging.getLogger(__name__)

    def write_actuator_event_to_csv(self, actuator_name, position):
        if self.streaming:
            event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            self.event_csv_writer.writerow([event_time, actuator_name, position])

    async def start_streaming(self):
        scan_rate = self.labjack.start_stream([sensor.streaming_address for sensor in self.analog_sensors])
        self.streaming = True
        header = ["time"] + [sensor.name for sensor in self.analog_sensors]
        converters = [lambda x: x] + [sensor.convert for sensor in self.analog_sensors]

        streaming_log_path = os.path.join(os.getcwd(), "backend/streaming")
        os.makedirs(streaming_log_path, exist_ok=True)
        streaming_csv_path = os.path.join(streaming_log_path, f"streaming_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        event_csv_path = os.path.join(streaming_log_path, f"event_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        # Open the CSV file and write the header
        self.csv_file = open(streaming_csv_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(header)

        # Open the event CSV file and write the header
        self.event_csv_file = open(event_csv_path, mode='w', newline='')
        self.event_csv_writer = csv.writer(self.event_csv_file)
        self.event_csv_writer.writerow(["time", "actuator", "position"])

        # Start the polling and logging in a separate task
        asyncio.create_task(self._poll_and_log_stream(converters))
        
        self.logger.info(f"Streaming started at: {scan_rate:.2f} Hz")

    async def _poll_and_log_stream(self, converters):
        while self.streaming:
            data = self.labjack.read_stream()
            
            # Convert the data to the correct format using NumPy
            converted_data = np.empty_like(data, dtype=object)
            
            for i, converter in enumerate(converters):
                converted_data[:, i] = converter(data[:, i])
            
            # Format timestamps to include milliseconds
            converted_data[:, 0] = [timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] for timestamp in converted_data[:, 0]]
            
            # Write the converted data to the CSV file
            self.csv_writer.writerows(converted_data)
            
            # Send the last row of data (latest timestamp) to the frontend
            latest_data = converted_data[-1]
            print(f"Latest data: {latest_data}, data shape = {converted_data.shape}")  # Replace with actual logging and sending to frontend

            await asyncio.sleep(1 / self.labjack.real_scan_rate * 0.1)  # Adjust sleep time based on the scan rate

    async def stop_streaming(self):
        self.streaming = False
        self.labjack.stop_stream()

        for sensor in self.analog_sensors:
            sensor.streaming_value = None

        if self.csv_file:
            self.csv_file.close()
        if self.event_csv_file:
            self.event_csv_file.close()

        self.logger.info(f"Streaming stopped and logs saved to: {self.csv_file.name}")