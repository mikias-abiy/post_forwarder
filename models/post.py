#!/usr/bin/python3

from telebot.async_telebot import AsyncTeleBot

"""
post.py: modules containes the defination of post class.
"""
import time
import datetime

from models.base_model import BaseModel
from models import storage

class Post(BaseModel):
    """
    Post:
        a class defination for Post object.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
    
    async def start(self, bot: AsyncTeleBot, to_gc):
        print("Posted started")
        
        print(datetime.datetime.now(), "\n", self.start_time)
        print(datetime.datetime.now() < self.start_time, "<")
        while datetime.datetime.now() < self.start_time:
            print("Sleeping 60 sec")
            time.sleep(60)

        print(datetime.datetime.now(), "\n", self.end_time)
        print(datetime.datetime.now() >= self.end_time, ">=")
        while datetime.datetime.now() <= self.end_time and self.status == 'active':
            print("Started posting")
            self.started = True
            for gc in to_gc:
                print("sending message")
                if self.message.text is None:
                    text = self.message.caption
                else:
                    text = self.message.text

                if self.message.video:
                    await bot.send_video(gc, self.message.video.file_id, caption=text)
                elif self.message.photo:
                    await bot.send_photo(gc, self.message.photo.file_id, caption=text)
                elif self.message.sticker:
                    await bot.send_sticker(gc, self.message.sticker.file_id)
                elif self.message.audio:
                    await bot.send_audio(gc, self.message.audio.file_id, caption=text)
                elif self.message.animation:
                    await bot.send_animation(gc, self.message.animation.file_id, caption=text)
                elif self.message.document:
                    await bot.send_document(gc, self.message.document.file_id, caption=text)
                else:
                    await bot.send_message(gc, text)
            time.sleep(self.repetition * 60 * 60)

        if datetime.datetime.now() >= self.end_time:
            print("Post removed")
            storage.remove(self)
        print("Exited Post")