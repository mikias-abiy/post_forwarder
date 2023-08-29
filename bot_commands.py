#!/usr/bin/python3
import re
import datetime
import asyncio

# Importing telbot modules and packages
from telebot import types
from telebot.util import quick_markup

# importing local modules and pakcages
from models.post import Post
from models import storage
import messages
import group_channel_manager as _gcm
from bot import bot

ADMIN = [6385140537]

@bot.message_handler(commands=['set_from'])
async def set_from(message):
    if message.from_user.id not in ADMIN:
        await bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return
    elif message.chat.type not in ["group", "supergroup"]:
        await bot.send_message(message.chat.id, "Use this command in group chat.")
        return

    _gcm.set_from(message.chat.id)
    await bot.send_message(message.chat.id, "This group is setted as the group from which messages are taken from.")


@bot.message_handler(commands=['add_to'])
async def add_to(message):
    if message.from_user.id not in ADMIN:
        await bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return
    elif message.chat.type not in ["group", "supergroup"]:
        await bot.send_message(message.chat.id, "Use this command in group chat.")
        return

    _gcm.add_to(message.chat.id)
    await bot.send_message(message.chat.id, "This group is added to the list of group which postes are forwarded to.")


@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document',
    'text', 'sticker'])
async def get_post_from(message):
    if message.from_user.id not in ADMIN or message.chat.id != _gcm.get_from():
        return

    post = Post()

    post.started = False
    post.stop = False
    post.status = 'active'
    post.message = message

    values = {}
    for i in range(0, 24):
        values[str(i)] = {'callback_data': f'repetition_{i}'}

    keyboard = quick_markup(values, row_width=5)

    text = f"""\
New post created.
ID: {post.id}

How often should the message be posted ?\
"""
    await bot.send_message(message.chat.id, text, reply_markup=keyboard)

@bot.message_handler(commands=['start'])
async def start(message):
    if message.chat.type == "private":
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button_add = \
            types.InlineKeyboardButton(text="➕ Add me to a group",
                                       url="\
https://t.me/post_forwarder_test_bot?startgroup=true\
")
        keyboard.row(button_add)
        await bot.send_message(message.chat.id, messages.INTRODUCTION, reply_markup=keyboard)
        return


@bot.callback_query_handler(func=lambda call: call.data.startswith('repetition_'))
async def callback_repetition(call):
    group_id_pattern = re.compile(r'ID: (\S+)')
    match = group_id_pattern.search(call.message.text)

    if match:
        post_id = match.group(1)
        print(f'Post ID: {post_id}')
    else:
        print('Post ID not found')

    repetition = int(call.data[11:])

    post = storage.all()[f"Post.{post_id}"]
    post.repetition = repetition

    values = {}
    ref_date = date = datetime.datetime.now()
    for i in range(0, 30 * 47, 30):
        delta = datetime.timedelta(minutes=i)
        date = ref_date + delta
        date = date.strftime("%H:%M:%S %d-%m-%y")
        values[date] = {'callback_data': f'start_time_{date}'}
    
    keyboard = quick_markup(values, row_width=2)
    
    text = f"""
ID: {post.id}

Choose a starting time
"""

    await bot.edit_message_text(text,
                          message_id=call.message.message_id,
                          chat_id=call.message.chat.id,
                          reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('start_time_'))
async def callback_start_time(call):
    group_id_pattern = re.compile(r'ID: (\S+)')
    match = group_id_pattern.search(call.message.text)

    if match:
        post_id = match.group(1)
        print(f'Post ID: {post_id}')
    else:
        print('Post ID not found')

    start_time = datetime.datetime.strptime(call.data[11:], "%H:%M:%S %d-%m-%y")

    post = storage.all()[f"Post.{post_id}"]
    post.start_time = start_time

    values = {}
    ref_date = datetime.datetime.now() + datetime.timedelta(days=1)
    for i in range(0, 31):
        delta = datetime.timedelta(days=i)
        date = ref_date + delta
        date = date.strftime("%d-%m-%y")
        values[date] = {'callback_data': f'end_time_{date}'}
    
    keyboard = quick_markup(values, row_width=3)
    
    text = f"""
ID: {post.id}

Choose an ending date
"""

    await bot.edit_message_text(text,
                          message_id=call.message.message_id,
                          chat_id=call.message.chat.id,
                          reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data.startswith('end_time_'))
async def callback_end_time(call):
    group_id_pattern = re.compile(r'ID: (\S+)')
    match = group_id_pattern.search(call.message.text)

    if match:
        post_id = match.group(1)
        print(f'Post ID: {post_id}')
    else:
        print('Post ID not found')

    end_time = datetime.datetime.strptime(call.data[9:], "%d-%m-%y")

    post = storage.all()[f"Post.{post_id}"]
    post.end_time = end_time
    post.save()
    await bot.delete_message(chat_id=call.message.chat.id,
                             message_id=call.message.message_id)
    await bot.send_message(call.message.chat.id, f"Post added successfully: \n{post.to_dict()}")
    asyncio.create_task(post.start(bot, _gcm.get_to()))