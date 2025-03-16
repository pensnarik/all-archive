#!/usr/bin/env python3

import os
import sys
import logging
import argparse

from aa.file import File
from aa.provider import FileSystemProvider
from aa.db import Database
from aa.mountpoints import Mountpoint, Mountpoints
from aa.image import ImageFile

logger = logging.getLogger("aa")

class App():

    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO, stream=sys.stdout)

        parser = argparse.ArgumentParser()
        parser.add_argument("--path", help="Source files path", required=True)

        self.args = parser.parse_args()

        self.db = Database()
        self.db.connect('postgresql://allarchive:allarchive@/allarchive')


    def run(self):
        self.path = os.path.abspath(self.args.path)

        print(f"The full path is: {self.path}")
        mps = Mountpoints(self.db)

        for mountpoint in mps.mountpoints:
            print(mountpoint)

        mp = mps.find_by_path(self.path)

        if mp is None:
            raise Exception(f"Could not find mountpoint for path: {self.path}")

        print(f"Found mountpoint for a given path: {mp}")

        mp.save()
        print(f"Counainer id == {mp.id}")

        provider = FileSystemProvider(
            self.path, mp
        )

        for path, url in provider.walk(self.path, self.path):
            print(path)

            fileobj = File(self.db, mp, path, url)
            fileobj.save()

            try:
                # Assume that file is an image
                imageobj = ImageFile(self.db, mp, fileobj, path, url)
                print(f"Format = {imageobj.im.format}")
                imageobj.save()
            except TypeError as e:
                # That is not an image
                logger.info(f"This is not an image: {e}")
            except PermissionError:
                print(f"Skipping {file} due to permission error")


if __name__ == "__main__":
    sys.exit(App().run())
