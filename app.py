#!/usr/bin/python3
import asyncio
import logging

# importing local modules and pakcages
import group_channel_manager as _gcm
import bot_commands
from bot_routines import post_starter
from bot import bot

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    _gcm.reload_gc()
    asyncio.run(bot.polling(), debug=True)
    asyncio.create_task(post_starter())