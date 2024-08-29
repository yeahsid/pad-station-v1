"""
IRIS_EVENT_HANDLER.py

Created on: 29/08/2024
Created by: Maisur Rahman

Helper file for setting up event based programming in IRIS
"""

import asyncio
import serial_asyncio

def InitIrisTasksSerial():
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


