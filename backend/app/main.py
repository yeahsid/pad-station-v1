from contextlib import asynccontextmanager
from fastapi import FastAPI, Path, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from app.hardware import LabJackConnection
from app.exceptions import DeviceNotOpenError, ValveNotFoundError, ServoNotFoundError, LabJackError, PressureSensorError, LoadCellError
from app.valve import ValveController, ValveState
from app.models import ValveResponse
from app.pressure_transducer import PressureTransducerSensor
from app.pilot_valve import PilotValveController
from app.thermocouple import ThermocoupleSensor
from app.load_cell import LoadCellSensor
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
import csv
import time
import json
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for the lifespan of the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application.

    Yields:
        None: This context manager does not return any value.

    """
    app.state = type('', (), {})()
    connection = LabJackConnection()
    app.state.valve_controller = ValveController(connection)
    app.state.pressure_transducer_sensor = PressureTransducerSensor(connection)
    app.state.thermocouple_sensor = ThermocoupleSensor(connection)
    app.state.pilot_valve_controller = PilotValveController(connection)
    app.state.load_cell_sensor = LoadCellSensor(connection)
    yield

app = FastAPI(lifespan=lifespan)


@app.exception_handler(DeviceNotOpenError)
@app.exception_handler(ValveNotFoundError)
@app.exception_handler(ServoNotFoundError)
@app.exception_handler(LabJackError)
@app.exception_handler(PressureSensorError)
@app.exception_handler(LoadCellError)
async def handle_custom_exceptions(request, exc):
    return JSONResponse(status_code=500, content={"message": str(exc)})

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Sent response: {response.status_code}")
    return response


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/valve/{valve_name}", response_model=ValveResponse)
async def actuate_main_valve(valve_name: str = Path(...), state: ValveState = Query(...)):
    app.state.valve_controller.actuate_valve(valve_name, state)
    return {"valve_name": valve_name, "feedback": None}


@app.get("/pilot_valve/{valve_name}", response_model=ValveResponse)
async def actuate_pilot_valve(background_tasks: BackgroundTasks, valve_name: str = Path(...), state: ValveState = Query(...)):
    background_tasks.add_task(
        app.state.pilot_valve_controller.actuate_valve, valve_name, state)

    return {"valve_name": valve_name, "feedback": state}


@app.get("/valve/{valve_name}/state", response_model=ValveResponse)
async def get_valve_state(valve_name: str = Path(...)):
    feedback = app.state.valve_controller.get_valve_state(valve_name)
    return {"valve_name": valve_name, "feedback": feedback}


@app.get("/pressure/{pressure_transducer_name}/feedback")
async def get_pressure_transducer_feedback(pressure_transducer_name: str = Path(...)):
    feedback = app.state.pressure_transducer_sensor.get_pressure_transducer_feedback(
        pressure_transducer_name)
    return {"pressure_transducer_name": pressure_transducer_name, "pressure": feedback}


@app.get("/pressure/{pressure_transducer_name}/datastream")
async def pressure_transducer_datastream(pressure_transducer_name: str):
    async def event_generator():
        async for data in app.state.pressure_transducer_sensor.pressure_transducer_datastream(pressure_transducer_name):
            yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/thermocouple/{thermocouple_name}/feedback")
async def get_thermocouple_feedback(thermocouple_name: str = Path(...)):
    feedback = app.state.thermocouple_sensor.get_thermocouple_temperature(
        thermocouple_name)
    return {"thermocouple_name": thermocouple_name, "temperature": feedback}


@app.get("/thermocouple/{thermocouple_name}/datastream")
async def thermocouple_datastream(thermocouple_name: str):
    async def event_generator():
        async for data in app.state.thermocouple_sensor.thermocouple_datastream(thermocouple_name):
            yield f"data: {data}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/ignition")
async def ignition(background_tasks: BackgroundTasks, delay: int = Query(4)):
    background_tasks.add_task(
        app.state.pilot_valve_controller.actuate_ignitor, delay)

    return {"message": "Ignition successful"}

@app.get("/log_data/start")
async def start_log_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(app.state.pressure_transducer_sensor.start_logging_all_sensors)
    background_tasks.add_task(app.state.thermocouple_sensor.start_logging_all_sensors)

@app.get("/load_cell/{load_cell_name}/feedback")
async def get_load_cell_mass(load_cell_name: str = Path(...)):
    feedback = app.state.load_cell_controller.get_load_cell_mass(
        load_cell_name)
    return {"load_cell_name": load_cell_name, "mass": feedback}

@app.get("/load_cell/{load_cell_name}/datastream")
async def load_cell_datastream(load_cell_name: str):
    async def event_generator():
        async for data in app.state.load_cell_controller.load_cell_datastream(load_cell_name):
            yield f"data: {data}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
