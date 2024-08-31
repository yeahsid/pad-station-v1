"""
IRIS_EVENT_HANDLER.py

Created on: 29/08/2024
Created by: Maisur Rahman

Helper file for setting up event based programming in IRIS
"""

import asyncio
import serial_asyncio

async def InitIrisTasksSerial():

    parse_event = asyncio.Event()
    respond_event = asyncio.Event()
    serial_event = asyncio.Event()


    ParseTask = asyncio.create_task(IrisSerialParseTask(parse_event))
    RespondTask = asyncio.create_task(IrisSerialResponderTask(respond_event))
    SerialTask = asyncio.create_task(IrisSerialReceiveTask(serial_event))
    
    while True:
        await ParseTask, RespondTask, SerialTask
        
    pass


async def IrisTransmit(notif: asyncio.Event):
    await notif.wait()

    pass

async def IrisSerialResponderTask(notif: asyncio.Event):
    await notif.wait()

    pass

async def IrisSerialReceiveTask(notif: asyncio.Event):
    await notif.wait()

    pass

async def IrisSerialParseTask(notif: asyncio.Event):
    await notif.wait()

    pass


