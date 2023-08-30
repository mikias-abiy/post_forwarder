#!/usr/bin/python3


from models.engine import file_storage
import os

os.system("rm storage.json")

storage = file_storage.FileStorage()
storage.reload()