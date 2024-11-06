from backend.actuators.abstractActuator import AbstractActuator
from backend.sensors.abstractSensors import AbstractAnalogSensor, AbstractDigitalSensor
from backend.control.labjack import LabJack
import asyncio
import numpy as np
import csv
from datetime import datetime
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

class StreamingLoggingController:

    def __init__(self, actuators: list[AbstractActuator], analog_sensors: list[AbstractAnalogSensor], digital_sensors: list[AbstractDigitalSensor], stream_scan_complete_event: asyncio.Event):
        self.labjack = LabJack()  # Access the singleton instance directly
        self.actuators = actuators
        self.analog_sensors = analog_sensors
        self.digital_sensors = digital_sensors
        self.stream_scan_complete_event = stream_scan_complete_event

        self.streaming = False
        self.streaming_sensors = []

        self.stream_csv_file = None
        self.csv_writer = None
        self.event_csv_file = None
        self.event_csv_writer = None

        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=1)

    def write_actuator_event_to_csv(self, actuator_name, position):
        if self.streaming:
            event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            self.event_csv_writer.writerow([event_time, actuator_name, position])

    async def start_streaming(self):
        self.streaming = True
        for sensor in self.analog_sensors:
            sensor.set_streaming()
        
        self.streaming_sensors = [sensor for sensor in self.analog_sensors if sensor.streaming_enabled]

        scan_rate = self.labjack.start_stream([sensor.streaming_address for sensor in self.streaming_sensors])

        header = ["time"] + [sensor.name for sensor in self.streaming_sensors]
        converters = [lambda x: x] + [sensor.convert for sensor in self.streaming_sensors]

        streaming_log_path = os.path.join(os.getcwd(), "streaming")
        os.makedirs(streaming_log_path, exist_ok=True)
        streaming_csv_path = os.path.join(streaming_log_path, f"streaming_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        event_csv_path = os.path.join(streaming_log_path, f"event_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        # Open the CSV file and write the header
        self.stream_csv_file = open(streaming_csv_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.stream_csv_file)
        self.csv_writer.writerow(header)

        # Open the event CSV file and write the header
        self.event_csv_file = open(event_csv_path, mode='w', newline='')
        self.event_csv_writer = csv.writer(self.event_csv_file)
        self.event_csv_writer.writerow(["time", "actuator", "position"])

        # Start the polling and logging in a separate thread
        loop = asyncio.get_event_loop()
        loop.run_in_executor(self.executor, self._poll_and_log_stream, converters)
        
        self.logger.info(f"Streaming started at: {scan_rate:.2f} Hz")

    def _poll_and_log_stream(self, converters):
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
            for i, sensor in enumerate(self.streaming_sensors):
                sensor.set_streaming(latest_data[i + 1])

            self.stream_scan_complete_event.set()
            time.sleep(1 / self.labjack.real_scan_rate)  # Adjust sleep time based on the scan rate

    async def stop_streaming(self):
        self.streaming = False
        self.labjack.stop_stream()

        for sensor in self.analog_sensors:
            sensor.deactivate_streaming()

        if self.stream_csv_file:
            self.stream_csv_file.close()
        if self.event_csv_file:
            self.event_csv_file.close()

        stream_file_name = os.path.basename(self.stream_csv_file.name)
        event_file_name = os.path.basename(self.event_csv_file.name)

        self.logger.info(f"Streaming stopped")
        self.logger.info(f"Streaming log saved to: {stream_file_name}")
        self.logger.info(f"Event log saved to: {event_file_name}")