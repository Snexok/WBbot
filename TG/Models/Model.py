import psycopg2
from psycopg2.extras import DictCursor


class Model:
    @staticmethod
    def execute(path, callback=None):
        with psycopg2.connect(dbname='WBBot', user='postgres',
                              password='root', host='localhost') as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(path)
                if callback:
                    return callback(cursor)