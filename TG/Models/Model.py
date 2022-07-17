from datetime import datetime

import psycopg2
from psycopg2.extras import DictCursor


class Model:
    COLUMNS = []
    table_name = ''

    def __init__(self):
        self.changed = False

    def __str__(self):
        res = ""
        for i, col in enumerate(self.COLUMNS):
            res += col + " = " + str(getattr(self, col)) + "; "
        return res

    @staticmethod
    def execute(path, callback=None):
        with psycopg2.connect(dbname='WBBot', user='postgres',
                              password='root', host='localhost') as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(path)
                if callback:
                    return callback(cursor)

    @staticmethod
    def fetchall(cursor):
        records = cursor.fetchall()
        return records

    def append(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, getattr(self, k) + v)
        self.changed = True

    def set(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.changed = True

    def insert(self):
        c = [col for col in self.COLUMNS if getattr(self, col) or type(getattr(self, col)) is bool]
        path = f"INSERT INTO {self.table_name} (" + ", ".join(c) + ") VALUES "
        if type(getattr(self, "id")) is int:
            path += f"((SELECT MAX(id)+1 FROM {self.table_name}), "
        elif type(getattr(self, "id")) is str:
            path += f"('{getattr(self, 'id')}', "
        for k in self.COLUMNS[1:]:
            v = getattr(self, k)
            if v or type(v) is bool:
                if type(v) is int:
                    path += f"{str(v)}, "
                elif type(v) is str or type(v) is datetime:
                    path += f"'{str(v)}', "
                elif type(v) is bool:
                    v = "TRUE" if v else "FALSE"
                    path += f"{v}, "
                elif type(v) is list:
                    if type(v[0]) is str:
                        if "," in str(v):
                            path += "ARRAY[" + ",".join("'" + a.replace(",", ";") + "'" for a in v) + "]::text[], "
                        else:
                            path += f"ARRAY{str(v)}::text[], "
                    elif type(v[0]) is int:
                        path += f"ARRAY{str(v)}::integer[], "
                    elif type(v[0]) is list:
                        if type(v[0][0]) is str:
                            if "," in str(v):
                                path += "ARRAY[" + ",".join("'" + a.replace(",", ";") + "'" for a in v) + "]::text[], "
                            else:
                                path += f"ARRAY{str(v)}::text[], "
                        elif type(v[0][0]) is int:
                            path += f"ARRAY{str(v)}::integer[][], "
        path = path[:-2]
        path += ")"
        print(path)
        self.execute(path)

    def update(self):
        path = f"UPDATE {self.table_name} SET "
        for k in self.COLUMNS[1:]:
            v = getattr(self, k)
            if v or type(v) is bool:
                if type(v) is int:
                    path += f"{k} = {str(v)}, "
                elif type(v) is str:
                    path += f"{k} = '{str(v)}', "
                elif type(v) is datetime.date:
                    path += f"{k} = '{str(v)}', "
                elif type(v) is datetime:
                    path += f"{k} = '{str(v)}', "
                elif type(v) is bool:
                    v = "TRUE" if v else "FALSE"
                    path += f"{k} = {v}, "
                elif type(v) is list:
                    if type(v[0]) is str:
                        if "," in str(v):
                            path += f"{k} = ARRAY[" + ",".join("'" + a.replace(",", ";") + "'" for a in v) + "]::text[], "
                        else:
                            path += f"{k} = ARRAY{str(v)}::text[], "
                    elif type(v[0]) is int:
                        path += f"{k} = ARRAY{str(v)}::integer[], "
        path = path[:-2]
        path += f" WHERE id='{str(self.id)}'"
        print(path)
        self.execute(path)


    def delete(self):
        path = f"DELETE FROM {self.table_name} WHERE id='{self.id}'"

        return self.execute(path)

    @classmethod
    def format_data(cls, data):
        res = []
        for d in data:
            obj = cls.single_model(*d)
            res += [obj]

        if res:
            return res
        else:
            return False