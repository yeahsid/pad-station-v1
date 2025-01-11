"""
Main entry point for the PadStation backend application.

This module sets up the FastAPI application, configures logging, and defines
the API endpoints for controlling actuators and handling WebSocket connections.
"""

from fastapi import FastAPI, WebSocket, BackgroundTasks, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
# from backend.control.padStationController import PadStationController
from backend.control.motorController import MotorController
from backend.control.newStreamingLoggingController import StreamingLoggingController
from backend.util.constants import BinaryPosition
from backend.actuators.pilotValve import PilotValve
from backend.actuators.activeVent import ActiveVent
from backend.actuators.hanbayValve import HanbayValve
from backend.actuators.relay import Relay
from backend.util.config import LabJackPeripherals, MotorControllerParams, MotorControllerPeripherals
from backend.actuators.dcMotorMC import DcMotor
from backend.actuators.servoMC import ServoMotor

import logging
import os
import asyncio
import re
from typing import Set
from contextlib import asynccontextmanager

class WebSocketHandler(logging.Handler):
    """
    Custom logging handler that broadcasts log messages to active WebSocket connections.
    """
    def __init__(self):
        super().__init__()
        self.active_websockets: Set[WebSocket] = set()

    def add_websocket(self, websocket: WebSocket):
        """
        Register a new WebSocket connection.

        Args:
            websocket (WebSocket): The WebSocket connection to add.
        """
        self.active_websockets.add(websocket)

    def remove_websocket(self, websocket: WebSocket):
        """
        Unregister a WebSocket connection.

        Args:
            websocket (WebSocket): The WebSocket connection to remove.
        """
        self.active_websockets.discard(websocket)

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to all active WebSocket connections.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        message = self.format(record)
        asyncio.create_task(self.send_to_websockets(message))

    async def send_to_websockets(self, message: str):
        """
        Send a log message to all registered WebSocket connections.

        Args:
            message (str): The log message to send.
        """
        websockets = list(self.active_websockets)
        for websocket in websockets:
            try:
                await websocket.send_text(message)
            except Exception:
                self.remove_websocket(websocket)

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    global motor_controller
    global mc_logging_controller
    
    motor_controller = await MotorController.get_connection()  # at some point document why this needs to be async
    mc_logging_controller = StreamingLoggingController(motor_controller)

    yield

# Configure logging
os.makedirs("logs", exist_ok=True)
websocket_handler = WebSocketHandler()
websocket_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s - %(message)s')
websocket_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)-34s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/backend.log"),
        logging.StreamHandler(),
        websocket_handler  # Add the custom WebSocketHandler
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://padstation-prod.goblin-decibel.ts.net:8080/", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    pad_station_controller = PadStationController()
    pad_logging_controller = StreamingLoggingController(pad_station_controller)
except:
    pass

motor_controller: MotorController  # defined later via the lifespan manager when we have an event loop running
mc_logging_controller: StreamingLoggingController


@app.get("/")
async def root():
    """
    Root endpoint to check LabJack connection status.

    Returns:
        dict: Message indicating connection status.
    """
    if pad_station_controller.labjack:
        return {"message": "LabJack connected successfully."}
    else:
        return {"message": "Failed to connect to LabJack."}
    

@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for sending sensor data to the frontend.

    Args:
        websocket (WebSocket): The WebSocket connection.
    """
    await websocket.accept()
    try:
        while True:
            # Create a separate task for gathering and compiling data
            # data_task_lj = asyncio.create_task(pad_station_controller.gather_and_compile_data_frontend())
            data_task_mc = asyncio.create_task(motor_controller.gather_and_compile_data_frontend())
            # data_lj = await data_task_lj
            data_mc = await data_task_mc

            await websocket.send_json(data_mc)
    except WebSocketDisconnect:
        logger.warning("Data WebSocket connection closed.")

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket endpoint for streaming log messages to the frontend.

    Args:
        websocket (WebSocket): The WebSocket connection.
    """
    await websocket.accept()
    websocket_handler.add_websocket(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection open
    except WebSocketDisconnect:
        websocket_handler.remove_websocket(websocket)
        logger.warning("Logs WebSocket connection closed.")

@app.post("/pilot-valve/open")
async def open_pilot_valve():
    """
    API endpoint to open the pilot valve.

    Returns:
        dict: Status message.
    """
    #pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    #await pv.actuate_valve(BinaryPosition.OPEN)

    motor: DcMotor = motor_controller.actuators[MotorControllerPeripherals.PILOT_VALVE.value]

    await motor.spin_motor(BinaryPosition.OPEN)
    return {"status": "Pilot valve opened"}

@app.post("/pilot-valve/close")
async def close_pilot_valve():
    """
    API endpoint to close the pilot valve.

    Returns:
        dict: Status message.
    """
    motor: DcMotor = motor_controller.actuators[MotorControllerPeripherals.PILOT_VALVE.value]

    await motor.spin_motor(BinaryPosition.CLOSE)
    return {"status": "Pilot valve closed"}

@app.post("/ignition/arm")
async def toggle_ignition_arm():
    """
    API endpoint to arm or disarm the ignition system.

    Returns:
        dict: Status message and current armed state.
    """
    pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    if not pv.armed:
        await pv.arm()
    else:
        await pv.disarm()
    return {"status": f"Ignition {'armed' if pv.armed else 'disarmed'}", "armed": pv.armed}

@app.post("/ignition/start")
async def start_ignition_sequence():
    """
    API endpoint to start the ignition sequence.

    Returns:
        dict: Status message.
    """
    pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    await pv.ignition_sequence()
    return {"status": "Ignition sequence started"}

@app.post("/ignition/abort")
async def abort_ignition_sequence():
    """
    API endpoint to abort the ignition sequence.

    Returns:
        dict: Status message.
    """
    pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    await pv.abort_ignition_sequence()
    return {"status": "Ignition sequence aborted"}

@app.post("/active-vent/open")
async def open_active_vent():
    """
    API endpoint to open the active vent.

    Returns:
        dict: Status message.
    """
    av: ServoMotor = motor_controller.actuators[MotorControllerPeripherals.ACTIVE_VENT.value]
    await av.actuate_servo(100)  # NOTE: I have no clue what it'll be, make this betterer

    return {"status": "Active vent opened"}

@app.post("/active-vent/close")
async def close_active_vent():
    """
    API endpoint to close the active vent.

    Returns:
        dict: Status message.
    """
    av: ServoMotor = motor_controller.actuators[MotorControllerPeripherals.ACTIVE_VENT.value]
    await av.actuate_servo(0)  # NOTE: I have no clue what it'll be, make this betterer

    return {"status": "Active vent closed"}

@app.post("/fill-valve/open")
async def open_fill_valve():
    """
    API endpoint to open the fill valve.

    Returns:
        dict: Status message.
    """
    fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
    await fv.actuate_valve(BinaryPosition.OPEN)
    return {"status": "Fill valve opened"}

@app.post("/fill-valve/close")
async def close_fill_valve():
    """
    API endpoint to close the fill valve.

    Returns:
        dict: Status message.
    """
    fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
    await fv.actuate_valve(BinaryPosition.CLOSE)
    return {"status": "Fill valve closed"}

@app.post("/dump-valve/open")
async def open_dump_valve():
    """
    API endpoint to open the dump valve.

    Returns:
        dict: Status message.
    """
    dv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.DUMP_VALVE.value]
    await dv.actuate_valve(BinaryPosition.OPEN)
    return {"status": "Dump valve opened"}

@app.post("/dump-valve/close")
async def close_dump_valve():
    """
    API endpoint to close the dump valve.

    Returns:
        dict: Status message.
    """
    dv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.DUMP_VALVE.value]
    await dv.actuate_valve(BinaryPosition.CLOSE)
    return {"status": "Dump valve closed"}

@app.post("/relay/ignitor/pulse")
async def pulse_ignitor_relay():
    """
    API endpoint to pulse the ignitor relay.

    Returns:
        dict: Status message.
    """
    ir: Relay = pad_station_controller.actuators[LabJackPeripherals.IGNITOR_RELAY.value]
    await ir.pulse(1)  # Assuming 1 second pulse time
    return {"status": "Ignitor relay pulsed"}

@app.post("/relay/qd/pulse")
async def pulse_qd_relay():
    """
    API endpoint to pulse the QD relay.

    Returns:
        dict: Status message.
    """
    qd: Relay = pad_station_controller.actuators[LabJackPeripherals.QD_RELAY.value]
    await qd.pulse(1)  # Assuming 1 second pulse time
    return {"status": "QD relay pulsed"}

@app.post("/relay/extra/pulse")
async def pulse_extra_relay():
    """
    API endpoint to pulse the extra relay.

    Returns:
        dict: Status message.
    """
    er: Relay = pad_station_controller.actuators[LabJackPeripherals.EXTRA_RELAY.value]
    await er.pulse(1)  # Assuming 1 second pulse time
    return {"status": "Extra relay pulsed"}

@app.post("/streaming/start")
async def start_streaming():
    """
    API endpoint to start data streaming.

    Returns:
        dict: Status message.
    """
    await pad_logging_controller.start_streaming()
    await mc_logging_controller.start_streaming()

    return {"status": "Streaming started"}

@app.post("/streaming/stop")
async def stop_streaming():
    """
    API endpoint to stop data streaming.

    Returns:
        dict: Status message.
    """
    await pad_logging_controller.stop_streaming()
    await mc_logging_controller.stop_streaming()

    return {"status": "Streaming stopped"}