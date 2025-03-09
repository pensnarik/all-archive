import os
import re
import subprocess

from aa.db import Database, UniqueViolation
from os.path import dirname, realpath

SUPPORTED_FS = ['ext3', 'ext4']


class Mountpoint():
    def __init__(self, db: Database, line: str):
        self.db = db
        # parse the line
        m = re.search(r'^([^\s]+) ([^\s]+) ([^\s]+) (.+)$', line)
        if m is None:
            raise TypeError(f"Could not parse mountpoint:\n`{line}`")

        self.device = m.group(1)
        self.mountpoint = m.group(2)
        self.type = m.group(3)
        self.mountopions = m.group(4)

        if self.type in SUPPORTED_FS:
            blkid = self.__blkid()
            self.uuid = blkid.get('UUID')
            self.label = blkid.get('LABEL')
        else:
            self.uuid = None
            self.label = None

    def __blkid(self):
        # Output example
        # /dev/nvme0n1p2: LABEL="root" UUID="4250c882-8b66-4d0d-a246-8142e4e6bab0" \
        # BLOCK_SIZE="4096" TYPE="ext4" PARTUUID="4fab0181-5e73-42de-be7c-98f9b72eccbf"
        result = {}

        blkid_path = os.path.join(dirname(realpath(__file__)), '..', 'blkid')
        output = subprocess.check_output([blkid_path, self.device]).decode('utf-8')

        for item in re.findall(r'([^=\s]+)="([^"]+)"', output):
            result[item[0]] = item[1]

        return result


    def __repr__(self):
        return f"{self.mountpoint} [{self.type}] [{self.uuid}]"


    def get_id(self, uuid: str):
        query = "select id from aa.storage_container where fs_uuid = %s"

        return self.db.fetchvalue(query, [uuid])


    def save(self):
        query = "insert into aa.storage_container (container_type, name, label, fs_uuid) " \
                "values (%s, %s, %s, %s) " \
                "returning id"

        self.id = self.get_id(self.uuid)

        if self.id is None:
            self.id = self.db.fetchvalue(query, (self.type, self.uuid, self.label, self.uuid))

        self.db.conn.commit()


class Mountpoints():

    def __init__(self, db: Database):
        self.db = db
        self.mountpoints = []
        self.list()

    def list(self):
        with open('/proc/mounts', 'rt') as f:
            for line in f.read().split('\n'):
                if line.strip() == '':
                    continue

                mp = Mountpoint(self.db, line)

                if mp.type in SUPPORTED_FS:
                    self.mountpoints.append(mp)

    def find_by_path(self, path: str):
        # Returns a mountpoint for a given path
        for mp in self.mountpoints:
            if path.startswith(mp.mountpoint):
                return mp

        return None
