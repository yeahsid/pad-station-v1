from backend.control.abstractSystemController import AbstractSystemController

import asyncio
from pathlib import Path
import csv
import logging
import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

class StreamingLoggingController:
    def __init__(self, system_controller: AbstractSystemController):
        self.sys_controller = system_controller

        self.is_streaming = False
        self.streaming_sensors = []

        self.stream_csv_file = None
        self.csv_writer = None
        self.event_csv_file = None
        self.event_csv_writer = None

        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=1)

        for actuator in self.sys_controller.actuators.values():
            actuator.register_event_handler(self.handle_actuator_event)

    async def start_streaming(self):
        scan_rate = self.sys_controller.start_sensor_streaming()

        if not self.sys_controller.streaming_sensors:  # no streaming sensors available
            return

        self.scan_rate = scan_rate

        # Prepare CSV headers and converter functions for each sensor
        header = ["time"] + [sensor.name for sensor in self.sys_controller.streaming_sensors]
        converters = [lambda x: x] + [sensor.convert for sensor in self.sys_controller.streaming_sensors]

        # Create directory for streaming logs if it doesn't exist
        streaming_log_path = Path.cwd() / "streaming"
        streaming_log_path.mkdir(exist_ok=True)

        # Define file paths with timestamps for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        streaming_csv_path = streaming_log_path / f"streaming_log_{timestamp}.csv"
        event_csv_path = streaming_log_path / f"event_log_{timestamp}.csv"

        # Open the CSV file and write the header
        self.stream_csv_file = open(streaming_csv_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.stream_csv_file)
        self.csv_writer.writerow(header)

        # Open the event CSV file and write the header
        self.event_csv_file = open(event_csv_path, mode='w', newline='')
        self.event_csv_writer = csv.writer(self.event_csv_file)
        self.event_csv_writer.writerow(["time", "actuator", "position"])

        # Start the polling and logging in a separate thread to prevent blocking
        loop = asyncio.get_event_loop()
        loop.run_in_executor(self.executor, self._poll_and_log_stream, converters)

        self.logger.info(f"Streaming started at: {scan_rate:.2f} Hz")
    
    async def handle_actuator_event(self, actuator, state):
        ...

    def _poll_and_log_stream(self, converters):
        while self.is_streaming:
            data = self.sys_controller.read_stream()

            # Initialize an empty array to store converted data
            converted_data = np.empty_like(data, dtype=object)
            
            # Apply converter functions to each column of data
            for i, converter in enumerate(converters):
                converted_data[:, i] = converter(data[:, i])
            
            # Format timestamps to include milliseconds for precision
            converted_data[:, 0] = [timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] for timestamp in converted_data[:, 0]]
            
            # Write the converted and formatted data to the CSV file
            self.csv_writer.writerows(converted_data)

            # Send the latest data point to the frontend for real-time updates
            latest_data = converted_data[-1]
            self.sys_controller.update_sensors_from_stream(latest_data)

            time.sleep(1 / self.scan_rate)

    async def stop_streaming(self):
        self.sys_controller.end_sensor_streaming()
        self.streaming = False

        if self.stream_csv_file:
            self.stream_csv_file.close()
        if self.event_csv_file:
            self.event_csv_file.close()
        
        self.logger.info("Streaming stopped")
        self.logger.info(f"Sensor stream log saved to: {self.stream_csv_file.name}")
        self.logger.info(f"Event log saved to: {self.event_csv_file.name}")