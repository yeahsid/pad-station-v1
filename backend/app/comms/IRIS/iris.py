"""
IRIS.py

Created on: 18/08/2024
Created by: Maisur Rahman

Helper Class for an IRIS instance
"""

from abc import ABC, abstractmethod
from queue import Queue

import iris_status
import iris_packet
import iris_rs422

class Iris: 
    """
    Represents an IRIS instance

    Attributes:

        devID (int): The ID of the device this instance of IRIS is running on.
        currentEventID (int): The current event's ID.
        txQueue (queue)
        rxQueue (queue)



    Methods:
        __init__(): Initialise the IRIS instance.
        irisSendRequest(ABC): Abstract method to send a request using any hardware interface.
        irisSendResponse(ABC): Abstract method to send a response using any hardware interface.
        irisSendMessage(ABC): Abstract method to send a message using any hardware interface.
        irisRespondtoReceiveEvent(ABC): Abstract method to respond to an incoming message.
    """

