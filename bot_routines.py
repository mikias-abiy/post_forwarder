#!/usr/bin/python3

import time
import threading

import group_channel_manager as _gcm

from models import storage
from bot import bot

def post_starter():
    """
    """
    print("Post forwarder routine started")
    while True:
        time.sleep(5)
        print("sleeping 5 second")
        posts = storage.all()
        print("Posts:", [value.to_dict() for value in posts.values()])
        for value in posts.values():
            if value.ready:
                if not value.started and value.status == 'active':
                    threading.Thread(target=value.start, args=(bot, _gcm.get_to)).start()