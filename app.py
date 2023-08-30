#!/usr/bin/python3
import asyncio
import threading
import logging

# importing local modules and pakcages
import group_channel_manager as _gcm
from bot_routines import post_starter
from command_handlesr import register_handlers
from bot import bot


logging.basicConfig(level=logging.DEBUG)


post_starter_thread = threading.Thread(target=post_starter)

if __name__ == '__main__':
    _gcm.reload_gc()
    register_handlers()

    post_starter_thread.start()

    bot.infinity_polling(none_stop=True)