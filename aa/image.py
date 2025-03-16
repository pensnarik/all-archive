import os
import re
import sys
import json
import argparse

from datetime import datetime
from enum import Enum
from PIL import Image, ExifTags, UnidentifiedImageError

from aa.file import File
from aa.db import Database
from aa.mountpoints import Mountpoint

class ImageFileType(Enum):
    unknown = -1
    invalid = 0
    jpeg = 1
    png = 2
    bmp = 3
    gif = 4
    webp = 5

class ImageFile():

    def __init__(self, db: Database, mp: Mountpoint, file: File, path: str, url: str):
        self.file = file
        self.exif = None
        self.time = None
        self.width = None
        self.height = None
        self.path = path
        self.db = db
        self.image_type = ImageFileType.unknown

        try:
            self.im = Image.open(self.path)
        except (UnidentifiedImageError, ValueError, OSError):
            raise TypeError(f"This is not an image")

        self.image_type = self.__get_type()

        try:
            self.exif = self.__read_exif()
        except OSError:
            self.image_type = ImageFileType.invalid

        self.time = self.__get_time()

        self.width = self.im.size[0]
        self.height = self.im.size[1]

    def __read_exif(self):
        if self.im.getexif() is None:
            return None

        return {
            ExifTags.TAGS[k]: v
            for k, v in self.im.getexif().items()
            if k in ExifTags.TAGS
        }

    def __get_time(self):
        if self.exif is None or not 'DateTimeOriginal' in self.exif:
            return None

        if self.exif['DateTimeOriginal'] == '0000:00:00 00:00:00':
            return None

        try:
            return datetime.strptime(self.exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
        except ValueError:
            return None

    def __get_type(self):
        if self.path.lower().endswith('.jpg') or \
           self.path.lower().endswith('.jpeg'):

            return ImageFileType.jpeg

        return ImageFileType.unknown

    def __get_exif_key(self, key: str) -> int:
        query_get = "select id from aa.exif_key where name = %s"
        query_ins = "insert into aa.exif_key (name) values (%s) returning id"

        id = self.db.fetchvalue(query_get, [key])

        if id is None:
            id = self.db.fetchvalue(query_ins, [key])

        return id

    def __save_exif_value(self, key_id: int, value: str):
        query_ins = "insert into aa.exif (image_file_id, key_id, value) " \
                "values(%s, %s, %s) " \
                "returning id"
        query_get = "select id from aa.exif "\
                    "where image_file_id = %s " \
                    "  and key_id = %s"

        if self.db.fetchvalue(query_get, [self.file.id, key_id]) is None:
            self.db.fetchvalue(query_ins, [self.file.id, key_id, str(value)])


    def save(self):
        self.file.save()

        query = "insert into aa.image_file(id, width, height, image_type) " \
                "values (%s, %s, %s, %s) " \
                "returning id"

        if self.db.fetchvalue("select 1 from aa.image_file where id = %s", [self.file.id]) is None:
            self.db.fetchone(query, [self.file.id, self.width, self.height, self.image_type])

        # Save EXIF
        print(self.exif)
        for k, v in self.exif.items():
            exif_key_id = self.__get_exif_key(k)
            self.__save_exif_value(exif_key_id, v)
