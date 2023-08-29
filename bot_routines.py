#!/usr/bin/python3

import time
import asyncio

import group_channel_manager as _gcm

from models import storage
from bot import bot

def post_starter():
    """
    """
    print("Post forwarder routine started")
    while True:
        time.sleep(60)
        posts = storage.all()
        for value in posts.values():
            if not value.started and value.status == 'active':
               asyncio.create_task(value.start(bot, _gcm.get_to()))