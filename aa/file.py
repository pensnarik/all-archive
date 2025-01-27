import os
import hashlib

from datetime import datetime, timezone

from aa.db import Database

class File():

    def __init__(self, db: Database, path: str):
        self.db = db
        self.path = path
        self.md5 = self.__get_md5()
        si = os.stat(self.path)
        self.size = si.st_size
        self.ctime = datetime.fromtimestamp(si.st_ctime, tz=timezone.utc)


    def __get_md5(self):
        with open(self.path, 'rb') as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)

            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)

        return file_hash.hexdigest()


    def save(self):
        query = "insert into aa.file(path, md5_hash, size, ctime) " \
                "values (%s, %s, %s, %s) " \
                "returning id"

        id = self.db.fetchone(query, (self.path, self.md5, self.size, self.ctime))

        self.db.conn.commit()