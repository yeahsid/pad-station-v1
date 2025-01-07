from backend.sensors.abstractSensors import AbstractAnalogSensor, AbstractDigitalSensor
from backend.actuators.abstractActuator import AbstractActuator

from abc import ABC, abstractmethod
import logging
from numpy import ndarray


class AbstractSystemController(ABC):
    def __init__(self):
        self.logger = logging.getLogger(__name__)  # TODO: check which name this is actually getting
        self.digital_sensors: ... = self._initialize_digital_sensors()
        self.analog_sensors: dict[str, AbstractAnalogSensor] = self._initialize_analog_sensors()
        self.actuators: ... = self._initialize_actuators()

        self.streaming_sensors: list[AbstractAnalogSensor] = []

    # @abstractmethod
    # async def actuated_event_handler(self, actuator: AbstractActuator, state):
    #     ...

    @abstractmethod
    def _initialize_digital_sensors(self) -> dict[str, AbstractDigitalSensor]:
        """
        Initializes all digital sensors used in the system.
        
        Returns:
            dict[str, AbstractDigitalSensor]: Dictionary of initialized digital sensors.
        """
        pass
    
    @abstractmethod
    def _initialize_analog_sensors(self) -> dict[str, AbstractAnalogSensor]:
        """
        Initializes all analog sensors used in the system.
        
        Returns:
            dict[str, AbstractAnalogSensor]: Dictionary of initialized analog sensors.
        """
        pass

    @abstractmethod
    def _initialize_actuators(self) -> dict[str, AbstractActuator]:
        """
        Initializes all actuators used in the system.
        
        Returns:
            dict[str, AbstractActuator]: Dictionary of initialized actuators.
        """
        pass
    
    @abstractmethod
    def start_sensor_streaming(self) -> tuple[list[AbstractAnalogSensor], int]:
        """
        Starts sensor streaming and returns the sensors actively streaming.

        Returns:
            tuple[list[AbstractAnalogSensor], int]: Streaming sensors and streaming rate.
        """
        # streaming_sensors = []

        # #for sensor in chain(self.analog_sensors.values(), self.digital_sensors.values()):
        # for sensor in self.analog_sensors.values():
        #     if sensor.streaming_enabled:
        #         sensor.set_streaming()
        #         streaming_sensors.append(sensor)
        
        # return 


        # for MC, in here we should spawn a task which is a loop calling gather_sensor_data
        pass
    
    @abstractmethod
    def read_stream(self) -> ndarray:
        # In MC this will simply loop through the sensors and get the current value
        # it's already being updated in the gather_sensor_data loop we spawn during start streaming
        # in the labjack it will be different
        pass

    @abstractmethod
    def update_sensors_from_stream(self, data: ndarray) -> None:
        # MC will do nothing here, padstation will update frontend stuff
        # make sure padstation sets the sensors_read event flag when it's done as streaming controller
        # will not do it anymore
        pass
    
    @abstractmethod
    def end_sensor_streaming(self):
        pass
