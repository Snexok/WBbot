from datetime import datetime

from TG.Models.Model import Model


class BotsWait(Model):
    COLUMNS = ['id', 'bot_name', 'event', 'start_datetime', 'end_datetime', 'wait', 'data']

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
        path = f"SELECT * FROM {cls.table_name} WHERE"
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
        path = f"DELETE FROM {cls.table_name} WHERE bot_name='{bot_name}' AND event='{event}'"

        return cls.format_data(cls.execute(path, cls.fetchall))
