from TG.Models.Model import Model


class BotsWait(Model):
    def __init__(self, id=0, bot_name='', event='', start_datetime='', end_datetime=''):
        super().__init__()
        self.id = id
        self.bot_name = bot_name
        self.event = event
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime


    @classmethod
    def load(cls, bot_name=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records
        if bot_name:
            path = "SELECT * FROM bots_wait WHERE bot_name='" + bot_name + "'"

        return cls.format_data(cls.execute(path, callback))

    @classmethod
    def insert(cls, bot_name, event, start_datetime, end_datetime):
        path = "INSERT INTO bots_wait (id, bot_name, event, start_datetime, end_datetime) VALUES "
        path += "((SELECT MAX(id)+1 FROM bots_wait), " + bot_name + ", '" + event + "', '" + start_datetime + "', '" + end_datetime + "')"
        print(path)
        cls.execute(path)

    @classmethod
    def format_data(cls, data):
        print(data)
        bots_wait = []
        for d in data:
            bot_wait = cls(*d)
            bots_wait += [bot_wait]

        if bots_wait:
            return bots_wait
        else:
            return False