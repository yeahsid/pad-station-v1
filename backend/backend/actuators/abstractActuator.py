from abc import ABC, abstractmethod
import logging
import asyncio
from backend.control.labjack import LabJack

class AbstractActuator(ABC):
    """
    Abstract base class for all actuators, providing common functionality.
    
    Attributes:
        logger (logging.Logger): Logger instance.
        name (str): Name of the actuator.
        labjack (LabJack): Singleton instance for LabJack device interaction.
        actuated_event (asyncio.Event): Event triggered when actuator is actuated.
        position (Optional[int]): Current position of the actuator.
        event_handlers (list): List of registered event handler callbacks.
    """
    logger = logging.getLogger(__name__)

    def __init__(self, name: str):
        """
        Initializes the AbstractActuator with a name and sets up the LabJack instance.
        Also attempts to run the setup coroutine.
        
        Args:
            name (str): Name of the actuator.
        """
        self.name = name
        self.position = None
        self.event_handlers = []

        self.logger = logging.getLogger(__name__)

        try:
            try:
                # Check for an existing event loop
                loop = asyncio.get_running_loop()
                loop.create_task(self.setup())  # Schedule setup in the running loop
            except RuntimeError:
                # If no loop is running, use asyncio.run()
                asyncio.run(self.setup())
            self.logger.info(f"{self.name} setup complete")
        except Exception as e:
            self.logger.error(f"{self.name} setup failed: {e}")

    @abstractmethod
    async def setup(self):
        """
        Abstract method to set up the actuator. Must be implemented by subclasses.
        """
        raise NotImplementedError()

    @abstractmethod
    async def move_to_safe_position(self):
        """
        Abstract method to move the actuator to a safe position. Must be implemented by subclasses.
        """
        raise NotImplementedError()
    
    def register_event_handler(self, handler):
        """
        Registers an event handler callback to be invoked when the actuator is actuated.
        
        Args:
            handler (Callable): Coroutine function to handle the event.
        """
        self.event_handlers.append(handler)

    def unregister_event_handler(self, handler):
        """
        Unregisters a previously registered event handler callback.
        
        Args:
            handler (Callable): The handler to remove.
        """
        self.event_handlers.remove(handler)

    async def trigger_actuated_event(self, position):
        """
        Triggers the actuated event and notifies all registered handlers.
        
        Args:
            position (int): The new position of the actuator.
        """
        self.position = position 
        for handler in self.event_handlers:
            await handler(self, position)
