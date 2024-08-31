"""
IRIS_EVENT_HANDLER.py

Created on: 29/08/2024
Created by: Maisur Rahman

Helper file for setting up event based programming in IRIS
"""

import asyncio
import serial_asyncio
from iris import Iris
import iris_serial

async def InitIrisTasksSerial():
    """
    Create the tasks required to run IRIS
    """

    receive_event = asyncio.Event()
    respond_event = asyncio.Event()
    transmit_event = asyncio.Event()


    receive_task = asyncio.create_task(IrisReceiveTask(receive_event))
    respond_task = asyncio.create_task(IrisRespondTask(respond_event))
    transmit_task = asyncio.create_task(IrisTransmitTask(transmit_event))
    
    while True:
        await receive_task, respond_task, transmit_task
        
    pass


async def IrisTransmitTask(notif: asyncio.Event, iris: Iris):

    # Retreive tx message off the queue
    transmit_packet = iris.tx_queue.get()

    #transmit using serial
    iris.interface.interfaceSendPacket(transmit_packet)
    await notif.wait()

    pass

async def IrisRespondTask(notif: asyncio.Event):
    await notif.wait()

    pass

async def IrisReceiveTask(notif: asyncio.Event):
    await notif.wait()

    pass

async def IrisParseTask(notif: asyncio.Event):
    await notif.wait()

    pass

