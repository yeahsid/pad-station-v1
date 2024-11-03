from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from backend.control.padStationController import PadStationController
from backend.util.config import FRONTEND_UPDATE_RATE
import asyncio

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
    return {"message": "Hello, FastAPI with Poetry!"}

@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await pad_station_controller.gather_and_compile_data_frontend()
            await websocket.send_json(data)
            await asyncio.sleep(1 / FRONTEND_UPDATE_RATE)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")
    finally:
        await websocket.close()
