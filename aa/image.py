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

class ImageFile(File):

    def __init__(self, db: Database, mp: Mountpoint, path: str):
        super().__init__(db, mp, path)

        self.exif = None
        self.time = None
        self.width = None
        self.height = None
        self.type = ImageFileType.unknown

        try:
            self.im = Image.open(self.path)
        except UnidentifiedImageError:
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
        if self.im._getexif() is None:
            return None

        return {
            ExifTags.TAGS[k]: v
            for k, v in self.im._getexif().items()
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

    def save(self):
        super().save()

        query = "insert into aa.image_file(id, width, height, image_type) " \
                "values (%s, %s, %s, %s) " \
                "returning id"

        self.db.fetchone(query, [self.id, self.width, self.height, self.type])
