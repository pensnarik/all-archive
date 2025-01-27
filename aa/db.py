import psycopg

from psycopg.errors import UniqueViolation

class Database():

    def __init__(self):
        pass


    def connect(self, dsn: str):
        self.conn = psycopg.connect(dsn)


    def execute(self, query: str, params: tuple=None):
        with self.conn.cusros() as cursor:
            cursor.execute(query, params)


    def fetch(self, query: str, params: tuple=None):
        result = []

        with self.conn.cusros() as cursor:
            cursor.execute(query, params)

            for row in cursor.fetchall():
                result.append(row)

        return result


    def fetchone(self, query: str, params: tuple=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)

            row = cursor.fetchone()

        return row


    def fetchvalue(self, query: str, params: tuple=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)

            row = cursor.fetchone()

        if row is not None:
            return row[0]

        return None
