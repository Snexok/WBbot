from datetime import datetime

from TG.Models.Model import Model

class BotWait(Model):
    COLUMNS = ['id', 'bot_name', 'event', 'start_datetime', 'end_datetime', 'wait', 'data']
    table_name = 'bots_wait'

    def __init__(self, id=1, bot_name='', event='', start_datetime='', end_datetime='', wait=False, data=''):
        super().__init__()
        self.id = id
        self.bot_name = bot_name
        self.event = event
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.wait = wait
        self.data = data

class BotsWait(Model):
    single_model = BotWait
    table_name = single_model.table_name

    @classmethod
    def load(cls, bot_name=None, event=None, limit=None, wait=None):
        path = f"SELECT * FROM {cls.table_name} WHERE "
        if bot_name:
            path += f"bot_name='{bot_name}' AND "
        if event:
            path += f"event='{event}' AND "
        if type(wait) == bool:
            wait = "TRUE" if wait else "FALSE"
            path += f"wait={wait} AND "

        path = path[:-5]

        if limit:
            path += f" LIMIT {str(limit)}"

        print(path)

        data = cls.format_data(cls.execute(path, cls.fetchall))

        if bot_name:
            if data:
                return data[0]
        return data

    @classmethod
    def delete(cls, bot_name, event):
        path = f"DELETE FROM {cls.table_name} WHERE bot_name='{bot_name}' AND event='{event}'"

        return cls.format_data(cls.execute(path, cls.fetchall))
