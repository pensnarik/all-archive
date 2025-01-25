import os

from typing import Callable

class Provider():

    def __init__(self):
        pass


class FileSystemProvider(Provider):

    def __init__(self, path: str, filter: Callable=lambda x: True):
        self.path = path
        self.filter = filter

    def get(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if self.filter(file):
                    yield os.path.join(root, file)
