from fastapi import FastAPI, WebSocket, BackgroundTasks, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from backend.control.padStationController import PadStationController
from backend.util.constants import BinaryPosition
from backend.actuators.pilotValve import PilotValve
from backend.actuators.activeVent import ActiveVent
from backend.actuators.hanbayValve import HanbayValve
from backend.actuators.relay import Relay
from backend.util.config import LabJackPeripherals
import logging
import os
import asyncio
import re

# Configure logging
os.makedirs("backend/logs", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)-34s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend/logs/backend.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://padstation-prod.goblin-decibel.ts.net:8080/", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pad_station_controller = PadStationController()

@app.get("/")
async def root():
    if pad_station_controller.labjack:
        return {"message": "LabJack connected successfully."}
    else:
        return {"message": "Failed to connect to LabJack."}


@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await pad_station_controller.gather_and_compile_data_frontend()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        logger.warning("Data WebSocket connection closed.")

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    log_file_path = "backend/logs/backend.log"
    # Define a regex pattern to match the log line
    log_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - [\w\.]+\s+- (\w+)\s+-\s+(.+)$')
    with open(log_file_path, "r") as log_file:
        log_file.seek(0, os.SEEK_END)  # Move to the end of the file
        try:
            while True:
                line = log_file.readline()
                if line:
                    line = line.strip()
                    # Use regex to parse the log line
                    match = log_pattern.match(line)
                    if match:
                        level = match.group(1)
                        message = match.group(2)
                        # Only send if level is higher than DEBUG
                        if level != "DEBUG":
                            await websocket.send_text(f"{level} - {message}")
                else:
                    try:
                        await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                    except asyncio.TimeoutError:
                        pass
                    await asyncio.sleep(0.1)  # Sleep briefly to avoid busy-waiting
        except WebSocketDisconnect:
            logger.warning("Logs WebSocket connection closed.")

@app.post("/pilot-valve/open")
async def open_pilot_valve():
    pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    await pv.actuate_valve(BinaryPosition.OPEN)
    return {"status": "Pilot valve opened"}

@app.post("/pilot-valve/close")
async def close_pilot_valve():
    pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    await pv.actuate_valve(BinaryPosition.CLOSE)
    return {"status": "Pilot valve closed"}

@app.post("/ignition/arm")
async def toggle_ignition_arm():
    pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    if not pv.armed:
        await pv.arm()
    else:
        await pv.disarm()
    return {"status": f"Ignition {'armed' if pv.armed else 'disarmed'}", "armed": pv.armed}

@app.post("/ignition/start")
async def start_ignition_sequence():
    pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    await pv.ignition_sequence()
    return {"status": "Ignition sequence started"}

@app.post("/ignition/abort")
async def abort_ignition_sequence():
    pv: PilotValve = pad_station_controller.actuators[LabJackPeripherals.PILOT_VALVE.value]
    await pv.abort_ignition_sequence()
    return {"status": "Ignition sequence aborted"}

@app.post("/active-vent/open")
async def open_active_vent():
    av: ActiveVent = pad_station_controller.actuators[LabJackPeripherals.ACTIVE_VENT.value]
    await av.move_to_open()
    return {"status": "Active vent opened"}

@app.post("/active-vent/close")
async def close_active_vent():
    av: ActiveVent = pad_station_controller.actuators[LabJackPeripherals.ACTIVE_VENT.value]
    await av.move_to_close()
    return {"status": "Active vent closed"}

@app.post("/fill-valve/open")
async def open_fill_valve():
    fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
    await fv.actuate_valve(BinaryPosition.OPEN)
    return {"status": "Fill valve opened"}

@app.post("/fill-valve/close")
async def close_fill_valve():
    fv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.FILL_VALVE.value]
    await fv.actuate_valve(BinaryPosition.CLOSE)
    return {"status": "Fill valve closed"}

@app.post("/dump-valve/open")
async def open_dump_valve():
    dv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.DUMP_VALVE.value]
    await dv.actuate_valve(BinaryPosition.OPEN)
    return {"status": "Dump valve opened"}

@app.post("/dump-valve/close")
async def close_dump_valve():
    dv: HanbayValve = pad_station_controller.actuators[LabJackPeripherals.DUMP_VALVE.value]
    await dv.actuate_valve(BinaryPosition.CLOSE)
    return {"status": "Dump valve closed"}

@app.post("/relay/ignitor/pulse")
async def pulse_ignitor_relay():
    ir: Relay = pad_station_controller.actuators[LabJackPeripherals.IGNITOR_RELAY.value]
    await ir.pulse(1)  # Assuming 1 second pulse time
    return {"status": "Ignitor relay pulsed"}

@app.post("/relay/qd/pulse")
async def pulse_qd_relay():
    qd: Relay = pad_station_controller.actuators[LabJackPeripherals.QD_RELAY.value]
    await qd.pulse(1)  # Assuming 1 second pulse time
    return {"status": "QD relay pulsed"}

@app.post("/relay/extra/pulse")
async def pulse_extra_relay():
    er: Relay = pad_station_controller.actuators[LabJackPeripherals.EXTRA_RELAY.value]
    await er.pulse(1)  # Assuming 1 second pulse time
    return {"status": "Extra relay pulsed"}

@app.post("/streaming/start")
async def start_streaming():
    await pad_station_controller.start_streaming()
    return {"status": "Streaming started"}

@app.post("/streaming/stop")
async def stop_streaming():
    await pad_station_controller.stop_streaming()
    return {"status": "Streaming stopped"}