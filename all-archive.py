#!/usr/bin/env python3

import os
import sys
import argparse

from aa.file import File
from aa.provider import FileSystemProvider
from aa.db import Database
from aa.mountpoints import Mountpoint, Mountpoints

class App():

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--path", help="Source files path", required=True)

        self.args = parser.parse_args()

        self.db = Database()
        self.db.connect('postgresql://allarchive:allarchive@/allarchive')

    def run(self):
        self.path = os.path.abspath(self.args.path)

        print(f"The full path is: {self.path}")
        mps = Mountpoints()

        for mountpoint in mps.mountpoints:
            print(mountpoint)

        mp = mps.find_by_path(self.path)

        if mp is None:
            raise Exception(f"Could not find mountpoint for path: {self.path}")

        print(f"Found mountpoint for a given path: {mp}")

        provider = FileSystemProvider(
            self.path
        )

        for file in provider.get():
            print(file)
            fileobj = File(self.db, file)
            fileobj.save()

if __name__ == "__main__":
    sys.exit(App().run())
