#!/usr/bin/env python3

import os
import sys
import argparse

class App():

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--path", help="Source files path")

        self.args = parser.parse_args()

    def run(self):
        print("App")

if __name__ == "__main__":
    sys.exit(App().run())
