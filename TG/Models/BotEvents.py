from datetime import datetime

from TG.Models.Model import Model

class BotEvent_Model(Model):
    COLUMNS = ['id', 'order_id', 'bot_name', 'event', 'sub_event', 'datetime_to_run', 'wait', 'running', 'pause', 'data',
               'start_datetime', 'end_datetime']
    table_name = 'bot_events'

    def __init__(self, id=1, order_id='', bot_name='', event='', sub_event='', datetime_to_run='', wait=False,
                 running=False, pause=False, data='', start_datetime='', end_datetime=''):
        super().__init__()
        self.id = id
        self.order_id = order_id
        self.bot_name = bot_name
        self.event = event
        self.sub_event = sub_event
        self.datetime_to_run = datetime_to_run
        self.wait = wait
        self.running = running
        self.pause = pause
        self.data = data
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    def delete(self):
        path = f"DELETE FROM {self.table_name} WHERE id={self.id}"

        return self.execute(path)

class BotsEvents_Model(Model):
    single_model = BotEvent_Model
    table_name = single_model.table_name

    exceptional_events = ['PAYMENT']

    @classmethod
    def load(cls, bot_name=None, event=None, limit=None, wait=None, order_id=None):
        path = f"SELECT * FROM {cls.table_name} WHERE wait=TRUE AND "
        if bot_name:
            path += f" bot_name='{bot_name}' AND "
        if event:
            path += f" event='{event}' AND "
        if type(wait) == bool:
            wait = "TRUE" if wait else "FALSE"
            path += f"wait={wait} AND "
        if order_id:
            path += f" order_id='{order_id}' AND "

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
    def load_last(cls):
        path = f"SELECT * FROM {cls.table_name} WHERE " \
               f"datetime_to_run = (SELECT MIN(datetime_to_run) FROM {cls.table_name} WHERE wait=TRUE AND running!=TRUE) " \
               f"AND datetime_to_run < '{str(datetime.now())}' AND wait=TRUE AND running!=TRUE AND " \
               f"event NOT IN {str(cls.exceptional_events).replace('[', '(').replace(']', ')')} " \
               f"LIMIT 1"
        data = cls.execute(path, cls.fetchall)
        if data:
            data = cls.format_data(data)[0]
        return data

    @classmethod
    def delete(cls, bot_name, event):
        path = f"DELETE FROM {cls.table_name} WHERE bot_name='{bot_name}' AND event='{event}'"

        return cls.format_data(cls.execute(path, cls.fetchall))

    @classmethod
    def check_exist_delivery_wait(cls, bot_name, order_id):
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
    bots_event = BotsEvents_Model.check('22')
    print(bots_event)