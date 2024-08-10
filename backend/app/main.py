

from contextlib import asynccontextmanager
from fastapi import FastAPI, Path, Query, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from app.comms.hardware import LabJackConnection
from app.comms.exceptions import DeviceNotOpenError, ValveNotFoundError, ServoNotFoundError, LabJackError, PressureSensorError, LoadCellError
from app.actuators.valve import ValveController, ValveState
from app.comms.models import ValveResponse
from app.sensors.pressure_transducer import PressureTransducerSensor
from app.actuators.pilot_valve import PilotValveController
from app.sensors.thermocouple import ThermocoupleSensor
from app.sensors.load_cell import LoadCellSensor
from app.actuators.relay import IgnitorRelayController
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import os
import asyncio



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = type('', (), {})()
    try:
        logging.info("Attempting to establish LabJack connection")
        connection = LabJackConnection()
        app.state.valve_controller = ValveController(connection)
        app.state.pressure_transducer_sensor = PressureTransducerSensor(
            connection)
        app.state.thermocouple_sensor = ThermocoupleSensor(connection)
        app.state.pilot_valve_controller = PilotValveController(connection)
        app.state.ignitor_relay_controller = IgnitorRelayController(connection)
        app.state.load_cell_sensor = LoadCellSensor(connection)
        app.state.labjack_connected = True
        logging.info("LabJack connection established")
    except Exception as e:
        logging.error(f"Failed to establish LabJack connection: {e}")
        raise e
    yield

app = FastAPI(lifespan=lifespan)


@app.exception_handler(DeviceNotOpenError)
@app.exception_handler(ValveNotFoundError)
@app.exception_handler(ServoNotFoundError)
@app.exception_handler(LabJackError)
@app.exception_handler(PressureSensorError)
@app.exception_handler(LoadCellError)
async def handle_custom_exceptions(exc):
    return JSONResponse(status_code=500, content={"message": str(exc)})

origins = [
    '*',
    "http://server.goblin-decibel.ts.net:3000"
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
    return {"labjack_connection": app.state.labjack_connected}


@app.get("/valve/{valve_name}", response_model=ValveResponse)
async def actuate_main_valve(valve_name: str = Path(...), state: ValveState = Query(...)):
    try:
        await app.state.valve_controller.actuate_valve(valve_name, state)
        return {"valve_name": valve_name, "feedback": None}
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")


@app.get("/pilot_valve/{valve_name}", response_model=ValveResponse)
async def actuate_pilot_valve(valve_name: str = Path(...), state: str = Query(...), timeout: int = Query(...)):
    try:
        await app.state.pilot_valve_controller.actuate_valve(valve_name, state, timeout)
        return {"valve_name": valve_name, "feedback": None}
    except Exception as ex:
        raise ex
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")

@app.get("/relays/{relay_name}", response_model=ValveResponse)
async def actuate_relay(relay_name: str = Path(...)):
    try:
        await app.state.ignitor_relay_controller.actuate_relay(relay_name)
        return {"valve_name": relay_name, "feedback": None}
    except Exception:
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")

# @app.get("/relays/{relay_name}", response_model=ValveResponse)
# async def actuate_relay(background_tasks: BackgroundTasks, relay_name: str = Path(...), state: ValveState = Query(...)):
#     background_tasks.add_task(
#         app.state.ignitor_relay_controller.actuate_relay, relay_name, state)

#     return {"relay_name": relay_name, "feedback": state}

@app.get("/valve/{valve_name}/state", response_model=ValveResponse)
async def get_valve_state(valve_name: str = Path(...)):
    try:
        feedback = app.state.valve_controller.get_valve_state(valve_name)
        return {"valve_name": valve_name, "feedback": feedback}
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")


@app.get("/pressure/{pressure_transducer_name}/feedback")
async def get_pressure_transducer_feedback(pressure_transducer_name: str = Path(...)):
    try:
        feedback = await app.state.pressure_transducer_sensor.get_pressure_transducer_feedback(
            pressure_transducer_name)
        return {"pressure_transducer_name": pressure_transducer_name, "pressure": feedback}
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")


@app.get("/pressure/{pressure_transducer_name}/datastream")
async def pressure_transducer_datastream(pressure_transducer_name: str):
    try:
        async def event_generator():
            async for data in app.state.pressure_transducer_sensor.pressure_transducer_datastream(pressure_transducer_name):
                yield f"data: {data}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")


@app.get("/thermocouple/{thermocouple_name}/feedback")
async def get_thermocouple_feedback(thermocouple_name: str = Path(...)):
    try:
        feedback = await app.state.thermocouple_sensor.get_thermocouple_temperature(
            thermocouple_name)

        return {"thermocouple_name": thermocouple_name, "temperature": feedback}
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")


@app.get("/thermocouple/{thermocouple_name}/datastream")
async def thermocouple_datastream(thermocouple_name: str):
    try:
        async def event_generator():
            async for data in app.state.thermocouple_sensor.thermocouple_datastream(thermocouple_name):
                yield f"data: {round(data, 1)}\n\n"
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e: 
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")


@app.get("/ignition")
async def ignition(background_tasks: BackgroundTasks, delay: int = Query(3)):
    try:
        background_tasks.add_task(
            app.state.pilot_valve_controller.actuate_ignitor, delay)

        return {"message": "Ignition successful"}
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")
    
@app.get("/load_cell_in/{load_cell_name}/feedback")
async def get_load_cell_mass(load_cell_name: str = Path(...)):
    try:
        feedback = await app.state.load_cell_sensor.get_load_cell_mass(
            load_cell_name)
        return {"load_cell_name": load_cell_name, "mass": feedback}
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")


@app.get("/load_cell_in/{load_cell_name}/datastream")
async def load_cell_datastream(load_cell_name: str):
    try:
        async def event_generator():
            async for data in app.state.load_cell_sensor.load_cell_datastream(load_cell_name):
                yield f"data: {data}\n\n"
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error. Check connection to LabJack.")


async def start_or_stop_sensor_logging(sensor, action: str):
    try:
        if action == "start":
            await sensor.start_logging_all_sensors()
        elif action == "stop":
            await sensor.end_logging_all_sensors()
    except Exception as e:
        logging.error(f"Failed to {action} logging for {sensor.__class__.__name__}: {e}")

    

async def operate_all_sensors_concurrently(action: str):
    tasks = []
    for sensor in [app.state.pressure_transducer_sensor, app.state.thermocouple_sensor , app.state.load_cell_sensor]:
        tasks.append(start_or_stop_sensor_logging(sensor, action))
    await asyncio.gather(*tasks)
    return {"message": f"Logging {action}ed for all sensors"}

@app.get("/log_data/start")
async def start_log_data(background_tasks: BackgroundTasks) -> dict:
    try:
        background_tasks.add_task(operate_all_sensors_concurrently, "start")
        return {"message": "Logging started"}
    except Exception as e:
        logging.error(f"Error starting log data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error. Check connection to LabJack.")

@app.get("/log_data/stop")
async def stop_log_data(background_tasks: BackgroundTasks) -> dict:
    try:
        background_tasks.add_task(operate_all_sensors_concurrently, "stop")
        return {"message": "Logging stopped"}
    except Exception as e:
        logging.error(f"Error stopping log data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error. Check connection to LabJack.")