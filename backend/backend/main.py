from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from backend.control.padStationController import PadStationController
from backend.util.constants import BinaryPosition
from backend.actuators.pilotValve import PilotValve
from backend.actuators.activeVent import ActiveVent
from backend.actuators.hanbayValve import HanbayValve
from backend.actuators.relay import Relay

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pad_station_controller = PadStationController()

@app.get("/")
async def root():

@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await pad_station_controller.gather_and_compile_data_frontend()
            await websocket.send_json(data)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        await websocket.close()

@app.post("/pilot-valve/open")
async def open_pilot_valve():
    pv: PilotValve = pad_station_controller.actuators["pilot_valve"]
    await pv.actuate_valve(BinaryPosition.OPEN)
    return {"status": "Pilot valve opened"}

@app.post("/pilot-valve/close")
async def close_pilot_valve():
    pv: PilotValve = pad_station_controller.actuators["pilot_valve"]
    await pv.actuate_valve(BinaryPosition.CLOSE)
    return {"status": "Pilot valve closed"}

@app.post("/active-vent/open")
async def open_active_vent():
    av: ActiveVent = pad_station_controller.actuators["active_vent"]
    await av.move_to_open()
    return {"status": "Active vent opened"}

@app.post("/active-vent/close")
async def close_active_vent():
    av: ActiveVent = pad_station_controller.actuators["active_vent"]
    await av.move_to_close()
    return {"status": "Active vent closed"}

@app.post("/fill-valve/open")
async def open_fill_valve():
    fv: HanbayValve = pad_station_controller.actuators["fill_valve"]
    await fv.actuate_valve(BinaryPosition.OPEN)
    return {"status": "Fill valve opened"}

@app.post("/fill-valve/close")
async def close_fill_valve():
    fv: HanbayValve = pad_station_controller.actuators["fill_valve"]
    await fv.actuate_valve(BinaryPosition.CLOSE)
    return {"status": "Fill valve closed"}

@app.post("/dump-valve/open")
async def open_dump_valve():
    dv: HanbayValve = pad_station_controller.actuators["dump_valve"]
    await dv.actuate_valve(BinaryPosition.OPEN)
    return {"status": "Dump valve opened"}

@app.post("/dump-valve/close")
async def close_dump_valve():
    dv: HanbayValve = pad_station_controller.actuators["dump_valve"]
    await dv.actuate_valve(BinaryPosition.CLOSE)
    return {"status": "Dump valve closed"}

@app.post("/relay/ignitor/pulse")
async def pulse_ignitor_relay():
    ir: Relay = pad_station_controller.actuators["ignitor_relay"]
    await ir.pulse(1)  # Assuming 1 second pulse time
    return {"status": "Ignitor relay pulsed"}

@app.post("/relay/qd/pulse")
async def pulse_qd_relay():
    qd: Relay = pad_station_controller.actuators["qd_relay"]
    await qd.pulse(1)  # Assuming 1 second pulse time
    return {"status": "QD relay pulsed"}

@app.post("/relay/extra/pulse")
async def pulse_extra_relay():
    er: Relay = pad_station_controller.actuators["extra_relay"]
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
