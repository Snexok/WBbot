from datetime import datetime

from TG.Models.Model import Model

class BotWait_Model(Model):
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

    def delete(self):
        path = f"DELETE FROM {self.table_name} WHERE id={self.id}"

        return self.execute(path)

class BotsWait_Model(Model):
    single_model = BotWait_Model
    table_name = single_model.table_name

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

        return cls.format_data(cls.execute(path, cls.fetchall))@classmethod

    @classmethod
    def load_last(cls):
        path = f"SELECT * FROM {cls.table_name} WHERE " \
               f"end_datetime = (SELECT MIN(end_datetime) FROM {cls.table_name}) " \
               f"AND end_datetime < '{str(datetime.now())}' LIMIT 1"
        data = cls.execute(path, cls.fetchall)
        if data:
            data = cls.format_data(data)[0]
        return data

    @classmethod
    def delete(cls, bot_name, event):
        path = f"DELETE FROM {cls.table_name} WHERE bot_name='{bot_name}' AND event='{event}'"

        return cls.format_data(cls.execute(path, cls.fetchall))

    @classmethod
    def check_exist_order_wait(cls, bot_name, order_id):
        path = f"SELECT t.* " \
               f"FROM (SELECT * FROM {cls.table_name} WHERE bot_name='{bot_name}') t " \
               f"WHERE data->>'id'='{str(order_id)}' AND wait=TRUE LIMIT 1"
        print(path)

        exist = cls.execute(path, cls.fetchall)

        if exist:
            return True
        else:
            return False

if __name__ == '__main__':
    bots_wait = BotsWait_Model.check('22')
    print(bots_wait)