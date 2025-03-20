import os
import re
import sys
import json
import logging
import argparse

from datetime import datetime
from enum import Enum
from PIL import Image, ExifTags, UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS

from aa.file import File
from aa.db import Database
from aa.mountpoints import Mountpoint

logger = logging.getLogger('aa')

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
            self.__read_exif()
        except OSError:
            self.image_type = ImageFileType.invalid

        self.time = self.__get_time()

        self.width = self.im.size[0]
        self.height = self.im.size[1]

    def __read_exif(self):
        try:
            exif_data = self.im._getexif()
        except AttributeError:
            return None

        if exif_data is None:
            return None

        self.exif = {}
        self.gps_info = None

        GPSINFO_TAG = next(
            tag for tag, name in TAGS.items() if name == "GPSInfo"
        )  # should be 34853

        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)

            if not isinstance(tag_name, str):
                logger.warning(f"Expected str as EXIF tag name, got: {tag_name.__class__.__name__}")
                continue

            self.exif[tag_name] = value

        self.gps_info = {}

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id in value:
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    self.gps_info[gps_tag] = value[gps_tag_id]

        return

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

        _value = str(value).replace('\x00', '')

        if self.db.fetchvalue(query_get, [self.file.id, key_id]) is None:
            self.db.fetchvalue(query_ins, [self.file.id, key_id, _value])


    def convert_to_decimal_degrees(self, degrees, minutes, seconds, ref):
        """Convert GPS coordinates from degrees, minutes, seconds to decimal degrees."""
        decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
        if ref in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    def get_gps_coordinates(self, gps_info):
        """Extract latitude and longitude from GPS info."""
        logger.info(f"{gps_info=}")
        try:
            # Extract latitude
            lat_degrees = gps_info['GPSLatitude'][0].numerator / gps_info['GPSLatitude'][0].denominator
            lat_minutes = gps_info['GPSLatitude'][1].numerator / gps_info['GPSLatitude'][1].denominator
            lat_seconds = gps_info['GPSLatitude'][2].numerator / gps_info['GPSLatitude'][2].denominator
            lat_ref = gps_info['GPSLatitudeRef']
            lat = self.convert_to_decimal_degrees(lat_degrees, lat_minutes, lat_seconds, lat_ref)

            # Extract longitude
            lon_degrees = gps_info['GPSLongitude'][0].numerator / gps_info['GPSLongitude'][0].denominator
            lon_minutes = gps_info['GPSLongitude'][1].numerator / gps_info['GPSLongitude'][1].denominator
            lon_seconds = gps_info['GPSLongitude'][2].numerator / gps_info['GPSLongitude'][2].denominator
            lon_ref = gps_info['GPSLongitudeRef']
            lon = self.convert_to_decimal_degrees(lon_degrees, lon_minutes, lon_seconds, lon_ref)

            return lat, lon
        except KeyError as e:
            logger.error(f"Missing required GPS tag: {e}")
            return None, None
        except ZeroDivisionError:
            logger.error("Could not get GPS coords - division by zero")
            return None, None


    def __save_coords(self):
        if self.exif is None or self.gps_info is None:
            return False

        if not isinstance(self.gps_info, dict):
            logger.warning(f"Unexpected GPSInfo format: {type(self.gps_info)}. Expected a dictionary.")
            return False

        query_get = "select id from aa.gps_coords where file_id = %s"
        query_ins = "insert into aa.gps_coords (file_id, lat, lon) " \
                    "values (%s, %s, %s) " \
                    "returning id"

        if self.db.fetchvalue(query_get, [self.file.id]) is not None:
            return

        lat_decimal, lon_decimal = self.get_gps_coordinates(self.gps_info)

        logger.info(f"Saving coords")

        self.db.fetchvalue(query_ins, [self.file.id, lat_decimal, lon_decimal])


    def save(self):
        self.file.save()

        query = "insert into aa.image_file(id, width, height, image_type) " \
                "values (%s, %s, %s, %s) " \
                "returning id"

        if self.db.fetchvalue("select 1 from aa.image_file where id = %s", [self.file.id]) is None:
            self.db.fetchone(query, [self.file.id, self.width, self.height, self.image_type])

        # Save EXIF
        if self.exif is not None:
            print(self.exif)
            for k, v in self.exif.items():
                exif_key_id = self.__get_exif_key(k)
                self.__save_exif_value(exif_key_id, v)

        self.__save_coords()

        self.db.conn.commit()
