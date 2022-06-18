from datetime import datetime

from TG.Models.Model import Model

COLUMNS = ['id', 'bot_name', 'event', 'start_datetime', 'end_datetime', 'wait', 'data']

class BotsWait(Model):
    def __init__(self, id=1, bot_name='', event='', start_datetime='', end_datetime='', wait=False, data=''):
        super().__init__()
        self.id = id
        self.bot_name = bot_name
        self.event = event
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.wait = wait
        self.data = data


    @classmethod
    def load(cls, bot_name=None, event=None, limit=None):
        path = "SELECT * FROM bots_wait WHERE"
        if bot_name:
            path += f" bot_name='{bot_name}', "
        elif event:
            path += f" event='{event}', "

        path = path[:-2]

        if limit:
            path += f" LIMIT {str(limit)}"

        return cls.format_data(cls.execute(path, cls.fetchall))

    @classmethod
    def delete(cls, bot_name, event):
        path = f"DELETE FROM bots_wait WHERE bot_name='{bot_name}' AND event='{event}'"

        return cls.format_data(cls.execute(path, cls.fetchall))

    def insert(self):
        c = [col for col in COLUMNS if getattr(self, col) or type(getattr(self, col)) is bool]
        path = "INSERT INTO bots_wait (" + ", ".join(c) + ") VALUES "
        path += "((SELECT MAX(id)+1 FROM bots_wait), "
        for k in COLUMNS[1:]:
            v = getattr(self, k)
            print(k, v, type(v))
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
                        path += f"ARRAY{str(v)}::text[], "
                    elif type(v[0]) is int:
                        path += f"ARRAY{str(v)}::integer[], "
        path = path[:-2]
        path += ")"
        print(path)
        self.execute(path)

    def update(self):
        path = "UPDATE bots_wait SET "
        for key in COLUMNS[1:]:
            value = getattr(self, key)
            print(key, value, type(value))
            if value or type(value) is bool:
                if type(value) is int:
                    path += f"{key} = { str(value)}, "
                elif type(value) is str:
                    path += f"{key} = '{str(value)}', "
                elif type(value) is datetime.date:
                    path += f"{key} = '{str(value)}', "
                elif type(value) is datetime:
                    path += f"{key} = '{str(value)}', "
                elif type(value) is bool:
                    value = "TRUE" if value else "FALSE"
                    path += f"{key} = {value}, "
                elif type(value) is list:
                    if type(value[0]) is str:
                        path += f"{key} = ARRAY{str(value)}::text[], "
                    elif type(value[0]) is int:
                        path += f"{key} = ARRAY{str(value)}::integer[], "
        path = path[:-2]
        path += f" WHERE id='{str(self.id)}'"
        self.execute(path)

    @classmethod
    def format_data(cls, data):
        bots_wait = []
        for d in data:
            bot_wait = cls(*d)
            bots_wait += [bot_wait]

        if bots_wait:
            return bots_wait
        else:
            return False