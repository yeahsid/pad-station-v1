from contextlib import asynccontextmanager
from fastapi import FastAPI, Path, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from app.hardware import LabJackConnection
from app.exceptions import DeviceNotOpenError, ValveNotFoundError, ServoNotFoundError, LabJackError, PressureSensorError
from app.valve import ValveController, ValveState
from app.servo import ServoController
from app.models import ValveResponse, ServoResponse
from app.pressure_transducer import PressureTransducerSensor
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state = type('', (), {})()
    connection = LabJackConnection()
    app.state.valve_controller = ValveController(connection)
    app.state.servo_controller = ServoController(connection)
    app.state.pressure_transducer_sensor = PressureTransducerSensor(connection)
    yield

app = FastAPI(lifespan=lifespan)


@app.exception_handler(DeviceNotOpenError)
@app.exception_handler(ValveNotFoundError)
@app.exception_handler(ServoNotFoundError)
@app.exception_handler(LabJackError)
@app.exception_handler(PressureSensorError)
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
async def actuate_valve(valve_name: str = Path(...), state: ValveState = Query(...)):
    app.state.valve_controller.actuate_valve(valve_name, state)
    return {"valve_name": valve_name, "feedback": None}


@app.get("/servo/{servo_name}", response_model=ServoResponse)
async def actuate_servo(servo_name: str = Path(...), duty_cycle: float = Query(...)):
    app.state.servo_controller.actuate_servo(servo_name, duty_cycle)
    return {"servo_name": servo_name, "feedback": None}


@app.get("/valve/{valve_name}/state", response_model=ValveResponse)
async def get_valve_state(valve_name: str = Path(...)):
    feedback = app.state.valve_controller.get_valve_state(valve_name)
    return {"valve_name": valve_name, "feedback": feedback}


@app.get("/servo/{servo_name}/feedback", response_model=ServoResponse)
async def get_servo_feedback(servo_name: str = Path(...)):
    feedback = app.state.servo_controller.get_servo_feedback(servo_name)
    return {"servo_name": servo_name, "feedback": feedback}


@app.get("/pressure/{pressure_transducer_name}/feedback")
async def get_pressure_transducer_feedback(pressure_transducer_name: str = Path(...)):
    feedback = app.state.pressure_transducer_sensor.get_pressure_transducer_feedback(
        pressure_transducer_name)
    return {"pressure_transducer_name": pressure_transducer_name, "pressure": feedback}


@app.get("/valve/{valve_name}/datastream")
async def valve_datastream(valve_name: str):
    async def event_generator():
        while True:
            feedback = app.state.valve_controller.get_valve_state(valve_name)
            yield f"data: {feedback}\n\n"
            # sleep for 1 second before sending the next update
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/pressure/{pressure_transducer_name}/datastream")
async def pressure_transducer_datastream(pressure_transducer_name: str):
    async def event_generator():
        async for data in app.state.pressure_transducer_sensor.pressure_transducer_datastream(pressure_transducer_name):
            yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")