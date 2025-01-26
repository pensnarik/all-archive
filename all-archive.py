#!/usr/bin/env python3

import os
import sys
import argparse

from aa.file import File
from aa.provider import FileSystemProvider
from aa.db import Database

class App():

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--path", help="Source files path", required=True)

        self.args = parser.parse_args()

        self.db = Database()
        self.db.connect('postgresql://allarchive:allarchive@/allarchive')

    def run(self):
        provider = FileSystemProvider(
            self.args.path,
            filter=lambda x: x.endswith('.jpg')
        )

        for file in provider.get():
            print(file)
            fileobj = File(file)

if __name__ == "__main__":
    sys.exit(App().run())
