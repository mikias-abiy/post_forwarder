#!/usr/bin/python3

"""
group_channel_manager.py: This module containes function and varibles that
manage the groups that are used in the posting process.
"""

import json


_FILE = "group_channel.json"

__TO = []
__FROM = None

def reload_gc():
    """
    """
    global __FROM
    global __TO

    try:
        with open(_FILE, 'r') as file:
            print("Reading privious group_channel.json file")
            gc = file.read()
            gc = json.loads(gc)
            __FROM = gc["__FROM"]
            print(f"group from set to: {__FROM}")
            __TO = gc["__TO"]
            print(f"group to set to: {__TO}")
    except FileNotFoundError:
        print("No previous group_channel.json file found.")

def save_gc():
    """
    """
    with open(_FILE, 'w') as file:
        gc = {"__TO": __TO, "__FROM": __FROM}
        gc = json.dumps(gc)
        file.write(gc)

def set_from(id):
    """
    """
    global __FROM
    __FROM = id
    save_gc()

def add_to(id):
    """
    """
    if id not in __TO:
        __TO.append(id)
    save_gc()

def remove_to(id):
    """
    """
    if id in __TO:
        __TO.remove(id)
    save_gc()

def get_to():
    """
    """
    return (__TO)

def get_from():
    """
    """
    return (__FROM)