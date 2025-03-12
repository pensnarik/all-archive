import os
import hashlib

from datetime import datetime, timezone

from aa.db import Database
from aa.mountpoints import Mountpoint

class File():

    def __init__(self, db: Database, mp: Mountpoint, path: str):
        self.db = db
        self.mp = mp
        self.path = path
        self.md5 = self.__get_md5()
        si = os.stat(self.path)
        self.size = si.st_size
        self.ctime = datetime.fromtimestamp(si.st_ctime, tz=timezone.utc)


    def __strip_mountpoint(self, path: str) -> str:
        if self.mp.mountpoint == '/':
            return path

        if not path.startswith(self.mp.mountpoint):
            raise Exception(f"Path must start with mountpoint")

        return path[len(self.mp.mountpoint):]


    def __get_md5(self):
        with open(self.path, 'rb') as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)

            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)

        return file_hash.hexdigest()


    def get_id(self):
        query = "select id from aa.file " \
                "where container_id = %s " \
                "  and path = %s"

        return self.db.fetchvalue(query, [self.mp.id, self.path])


    def save(self):
        query = "insert into aa.file(container_id, path, md5_hash, size, ctime) " \
                "values (%s, %s, %s, %s, %s) " \
                "returning id"

        self.id = self.get_id()

        if self.id is None:
            self.id = self.db.fetchvalue(
                query, (self.mp.id, self.__strip_mountpoint(self.path), self.md5, self.size, self.ctime)
            )

        print(f"file.id == {self.id}")

        self.db.conn.commit()
