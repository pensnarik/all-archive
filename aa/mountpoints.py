import os
import re


class Mountpoint():
    def __init__(self, line: str):
        # parse the line
        m = re.search(r'^([^\s]+) ([^\s]+) ([^\s]+) (.+)$', line)
        if m is None:
            raise TypeError(f"Could not parse mountpoint:\n`{line}`")

        self.device = m.group(1)
        self.mountpoint = m.group(2)
        self.type = m.group(3)
        self.mountopions = m.group(4)

    def __repr__(self):
        return f"{self.mountpoint} [{self.type}]"


class Mountpoints():

    def __init__(self):
        self.mountpoints = []
        self.list()

    def list(self):
        with open('/proc/mounts', 'rt') as f:
            for line in f.read().split('\n'):
                if line.strip() == '':
                    continue

                mp = Mountpoint(line)

                if mp.type in ['ext3', 'ext4']:
                    self.mountpoints.append(Mountpoint(line))

    def find_by_path(self, path: str):
        # Returns a mountpoint for a given path
        for mp in self.mountpoints:
            if path.startswith(mp.mountpoint):
                return mp

        return None
