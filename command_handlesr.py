#!/usr/bin/python3
import re
import datetime
import asyncio
import logging


# Importing telbot modules and packages
from telebot import types
from telebot.util import quick_markup


# importing local modules and pakcages
import messages
import group_channel_manager as _gcm
from models.post import Post
from models import storage
from bot import bot

logging.basicConfig(level=logging.DEBUG)

ADMIN = [6385140537, 386758208]

def set_from(message: types.Message):
    if message.from_user.id not in ADMIN:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return
    elif message.chat.type not in ["group", "supergroup"]:
        bot.send_message(message.chat.id, "Use this command in group chat.")
        return

    _gcm.set_from(message.chat.id)
    bot.send_message(message.chat.id, "This group is setted as the group from which messages are taken from.")


def add_to(message: types.Message):
    if message.from_user.id not in ADMIN:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return
    elif message.chat.type not in ["group", "supergroup"]:
        bot.send_message(message.chat.id, "Use this command in group chat.")
        return

    _gcm.add_to(message.chat.id)
    bot.send_message(message.chat.id, "This group is added to the list of group which postes are forwarded to.")


def get_post_from(message: types.Message):
    if message.from_user.id not in ADMIN or message.chat.id != _gcm.get_from():
        return

    post = Post()

    post.ready = False
    post.started = False
    post.stop = False
    post.restart = False
    post.status = 'inactive'
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
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

def command_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_add = \
        types.InlineKeyboardButton(text="➕ Add me to a group",
                                   url="\
https://t.me/post_forwarder_test_bot?startgroup=true\
")
    keyboard.row(button_add)
    bot.send_message(message.chat.id, messages.INTRODUCTION, reply_markup=keyboard)


def command_status(message: types.Message, edit=None):
    if message.from_user.id not in ADMIN and message.from_user.id != bot.get_me().id:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")
        return
    posts = storage.all()

    values = []

    if len(posts):
        text = "<b>Posts:</b>\n\n"
    else:
        text = "<b>No Posts</b>"
    i = 1
    for value in posts.values():
        text += f"<b>Post {i}</b>\n"
        text += f"<b>ID</b>: {value.id}\n"
        text += f"<b>Repetition</b>: every <code>{value.repetition}</code> hr\n"
        text += f"<b>Status</b>: <code>{value.status}</code>\n"
        begining = ""
        if value.message.text:
            begining = value.message.text
            if len(value.message.text) < 10:
                begining = begining[0:len(value.message.text)]
            else:
                begining = begining[0:10]
        elif value.message.caption:
            begining = value.message.caption
            if len(value.message.caption) < 10:
                begining = begining[0:len(value.message.caption)]
            else:
                begining = begining[0:10]
        text += f"<b>Message</b>: {begining}...\n\n"
        values.append(types.InlineKeyboardButton(text=f"Post {i}", callback_data=f"edit_{value.id}"))
        values.append(types.InlineKeyboardButton(text=f"{'ON' if value.status == 'inactive' else 'OFF'}", callback_data=f"update_status_{value.id}"))
        values.append(types.InlineKeyboardButton(text=f"🗑", callback_data=f"delete_{value.id}"))
        i += 1

    keyboard = None
    if len(posts):
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(*values)

    if not edit:
        bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode="HTML")
    else:
        bot.edit_message_text(text=text,
                              chat_id=message.chat.id,
                              message_id=message.message_id,
                              reply_markup=keyboard,
                              parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith('repetition_'))
def callback_repetition(call):
    post_id_pattern = re.compile(r'ID: (\S+)')
    match = post_id_pattern.search(call.message.text)

    if match:
        post_id = match.group(1)
        print(f'Post ID: {post_id}')
    else:
        print('Post ID not found')

    if call.data[11] == 'e' and call.data[12] == '_':
        repetition = int(call.data[13:])
    else:
        repetition = int(call.data[11:])


    post = storage.all()[f"Post.{post_id}"]
    post.repetition = repetition
    post.save()

    if call.data[11] == 'e' and call.data[12] == '_':
        call.data = f"edit_{post_id}"
        post.restart = True
        post.save()
        edit_post(call, True)
        return

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

    bot.edit_message_text(text,
                          message_id=call.message.message_id,
                          chat_id=call.message.chat.id,
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('start_time_'))
def callback_start_time(call):
    group_id_pattern = re.compile(r'ID: (\S+)')
    match = group_id_pattern.search(call.message.text)

    if match:
        post_id = match.group(1)
        print(f'Post ID: {post_id}')
    else:
        print('Post ID not found')

    if call.data[11] == 'e' and call.data[12] == '_':
        start_time = datetime.datetime.strptime(call.data[13:], "%H:%M:%S %d-%m-%y")
    else:
        start_time = datetime.datetime.strptime(call.data[11:], "%H:%M:%S %d-%m-%y")

        

    post = storage.all()[f"Post.{post_id}"]
    post.start_time = start_time
    post.save()

    if call.data[11] == 'e' and call.data[12] == '_':
        call.data = f"edit_{post_id}"
        post.restart = True
        post.save()
        edit_post(call, True)
        return

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

    bot.edit_message_text(text,
                          message_id=call.message.message_id,
                          chat_id=call.message.chat.id,
                          reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data.startswith('end_time_'))
def callback_end_time(call):
    group_id_pattern = re.compile(r'ID: (\S+)')
    match = group_id_pattern.search(call.message.text)

    if match:
        post_id = match.group(1)
        print(f'Post ID: {post_id}')
    else:
        print('Post ID not found')

    if call.data[9] == 'e' and call.data[10] == '_':
        end_time = datetime.datetime.strptime(call.data[11:], "%d-%m-%y")
    else:
        end_time = datetime.datetime.strptime(call.data[9:], "%d-%m-%y")

    post = storage.all()[f"Post.{post_id}"]
    post.end_time = end_time
    post.ready = True
    post.save()

    if call.data[9] == 'e' and call.data[10] == '_':
        call.data = f"edit_{post_id}"
        post.restart = True
        post.save()
        edit_post(call, True)
        return

    bot.delete_message(chat_id=call.message.chat.id,
                         message_id=call.message.message_id)
    bot.send_message(call.message.chat.id, f"Post added successfully: \n{post.to_dict()}")



@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def edit_post(call, custom=None):
    if custom:
        datalen = len(call.data)

        for i in range(datalen, 0, -1):
            if call.data[i - 1] == "_":
                post_id = call.data[i:]
                break
    else:
        post_id = call.data[5:]

    post = storage.all()[f"Post.{post_id}"]
    text = ""
    text += f"<b>ID</b>: {post.id}\n"
    text += f"<b>Repetition</b>: every <code>{post.repetition}</code> hr\n"
    text += f"<b>Status</b>: <code>{post.status}</code>\n"
    begining = ""
    if post.message.text:
        begining = post.message.text
        if len(post.message.text) < 10:
            begining = begining[0:len(post.message.text)]
        else:
            begining = begining[0:10]
    elif post.message.caption:
        begining = post.message.caption
        if len(post.message.caption) < 10:
            begining = begining[0:len(post.message.caption)]
        else:
            begining = begining[0:10]
    text += f"<b>Message</b>: {begining}...\n\n"


    values = {
        "Start time": {"callback_data": f"update_start_time_{post.id}"},
        "Repetition": {"callback_data": f"update_repetition_{post.id}"},
        "End time": {"callback_data": f"update_end_time_{post.id}"},
        "Back": {"callback_data": "back_status"}
    }
    keyboard = quick_markup(values, row_width=3)

    bot.edit_message_text(text,
                          message_id=call.message.message_id,
                          chat_id=call.message.chat.id,
                          reply_markup=keyboard,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("back_"))
def back(call):
    page = call.data[5:]

    if page == "status":
        command_status(call.message, True)
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith("update_status_"))
def update_status(call):
    post_id = call.data[14:]

    post = storage.all()[f"Post.{post_id}"]
    post.status = 'active' if post.status == 'inactive' else 'inactive'
    post.save()

    command_status(call.message, True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def delete_post(call):
    post_id = call.data[7:]
    
    post = storage.all()[f"Post.{post_id}"]
    post.stop = True
    storage.remove(post)
    storage.save()

    command_status(call.message, True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("update_"))
def update_post(call):
    datalen = len(call.data)

    for i in range(datalen, 0, -1):
        if call.data[i - 1] == "_":
            post_id = call.data[i:]
            action = call.data[7:i - 1]
            break

    post = storage.all()[f"Post.{post_id}"]

    print(action)
    if action == "start_time":
        values = {}
        ref_date = date = datetime.datetime.now()
        for i in range(0, 30 * 47, 30):
            delta = datetime.timedelta(minutes=i)
            date = ref_date + delta
            date = date.strftime("%H:%M:%S %d-%m-%y")
            values[date] = {'callback_data': f'start_time_e_{date}'}
    
        keyboard = quick_markup(values, row_width=2)
    
        text = f"""
ID: {post.id}

Choose a starting time
"""

        bot.edit_message_text(text,
                          message_id=call.message.message_id,
                          chat_id=call.message.chat.id,
                          reply_markup=keyboard)
    elif action == "end_time":
        values = {}
        ref_date = datetime.datetime.now() + datetime.timedelta(days=1)
        for i in range(0, 31):
            delta = datetime.timedelta(days=i)
            date = ref_date + delta
            date = date.strftime("%d-%m-%y")
            values[date] = {'callback_data': f'end_time_e_{date}'}
    
        keyboard = quick_markup(values, row_width=3)
    
        text = f"""
ID: {post.id}

Choose an ending date
"""

        bot.edit_message_text(text,
                              message_id=call.message.message_id,
                              chat_id=call.message.chat.id,
                              reply_markup=keyboard)
    elif action == "repetition":
        values = {}
        for i in range(0, 24):
            values[str(i)] = {'callback_data': f'repetition_e_{i}'}

        keyboard = quick_markup(values, row_width=5)

        text = f"""\
New post created.
ID: {post.id}

How often should the message be posted ?\
"""        
        bot.edit_message_text(text,
                              message_id=call.message.message_id,
                              chat_id=call.message.chat.id,
                              reply_markup=keyboard)

def register_handlers():
    bot.register_message_handler(command_start, func=lambda message: message.text == '/start')
    bot.register_message_handler(command_status, func=lambda message: message.text == '/status')
    bot.register_message_handler(get_post_from, content_types=['audio', 'photo', 'voice', 'video', 'document',
    'text', 'sticker'], func=lambda message: message.text[0] != '/')
    bot.register_message_handler(set_from, func=lambda message: message.text == '/set_from')
    bot.register_message_handler(add_to, func=lambda message: message.text == '/add_to')
    