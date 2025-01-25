#!/usr/bin/env python3

import os
import sys
import argparse

from aa.provider import FileSystemProvider

class App():

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--path", help="Source files path", required=True)

        self.args = parser.parse_args()

    def run(self):
        provider = FileSystemProvider(
            self.args.path,
            filter=lambda x: x.endswith('.jpg')
        )

        for file in provider.get():
            print(file)


if __name__ == "__main__":
    sys.exit(App().run())
