import os

from stat import S_ISSOCK, S_ISLNK, S_ISCHR

from typing import Callable

from aa.mountpoints import Mountpoint

class Provider():

    def __init__(self):
        pass


class FileSystemProvider(Provider):

    def __init__(self, path: str, mp: Mountpoint, filter: Callable=lambda x: True):
        self.path = path
        self.mp = mp
        self.filter = filter


    def get(self):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                mode = os.lstat(os.path.join(root, file)).st_mode

                if self.filter(file) and not S_ISSOCK(mode) and not S_ISLNK(mode) and not S_ISCHR(mode):
                    yield os.path.join(root, file)
