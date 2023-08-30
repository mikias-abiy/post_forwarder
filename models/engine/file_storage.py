#!/usr/bin/python3

"""
file_storage:
    This module holds the defination of the class FileStorage
    which handles the storage of objects.
"""

import json


class FileStorage:
    """
    FileStorage: handles object storage persistency

    Attributes:
        __file_path (str): path to the json file holding the objects
                           json representation.
       __objects (dict): Dictionary holding the objects.
    """

    __objects = {}
    __file_path = 'storage.json'

    def all(self):
        """
        all(self):
            Returns dictionary of the objects stored.

        Return:
            Dictionry of the the stored objects.
        """
        return (FileStorage.__objects)

    def new(self, obj):
        """
        new:
            Inserts new object to the collection of objects.

        Args:
            obj: The object to be stored.

        Return:
            None.
        """
        FileStorage.__objects[f'{type(obj).__name__}.{obj.id}'] = obj
    
    def remove(self, obj):
        """
        remove:
            Removes an object from the collection of objects.

        Args:
            obj: The object to be stored.

        Return:
            None.
        """
        FileStorage.__objects.pop(f'{type(obj).__name__}.{obj.id}')
        self.save()

    def save(self):
        """
        save(self):
            Saves the objects collection dictionary in to a file
            after converting it to a json representation.

        Return:
            None.
        """
        with open(FileStorage.__file_path, 'w') as file:
            to_serialize = FileStorage.__objects.copy()
            for key in to_serialize.keys():
                to_serialize[key] = to_serialize[key].to_dict()
            file.write(json.dumps(to_serialize))

    def reload(self):
        """
        reload(self):
            Reloads the objects from the last saved file that
            that contains the json representation of the objects.
        """
        try:
            with open(FileStorage.__file_path, 'r') as file:
                json_str = file.read()
                if len(json_str):
                    _raw = json.loads(json_str)
                    if len(FileStorage.__objects):
                        for key in _raw.keys():
                            for key_in in FileStorage.__objects:
                                if (key == key_in):
                                    FileStorage.__objects[key_in].update(**_raw[key])
                                    break
                        return
    
                    for key in _raw.keys():
                        if _raw[key]['__class__'] == 'Post':
                            from models.post import Post
                            _raw[key] = Post(**_raw[key])
                    FileStorage.__objects = _raw
        except FileNotFoundError:
            pass