import psycopg2
from psycopg2.extras import DictCursor


class Model:
    def __init__(self):
        self.changed = False

    @staticmethod
    async def execute(path, callback=None):
        with psycopg2.connect(dbname='WBBot', user='postgres',
                              password='root', host='localhost') as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(path)
                if callback:
                    return callback(cursor)

    def append(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, getattr(self, k) + v)
        self.changed = True

    def set(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.changed = True
