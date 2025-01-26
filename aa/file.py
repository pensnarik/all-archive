from aa.db import Database

class File():

    def __init__(self, db: Database, path: str):
        self.path = path
