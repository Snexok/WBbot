from TG.Models.Model import Model


class Bot(Model):
    COLUMNS = ['id', 'name', 'addresses', 'number', 'username', 'type', 'inns', 'status', 'author', 'balance']
    table_name = 'bots'

    def __init__(self, id='0', name='', addresses=[], number='', username='', type='', inns=[], status='', author='', balance=''):
        super().__init__()
        self.id = id
        self.name = name
        self.addresses = addresses
        self.number = number
        self.username = username
        self.type = type
        self.inns = inns
        self.status = status
        self.author = author
        self.balance = balance

class Bots(Model):
    single_model = Bot
    table_name = single_model.table_name

    @classmethod
    def load(cls, name=None, limit=None, _type=None, balance=None):
        path = f"SELECT * FROM {cls.table_name} "

        if name:
            path += f"WHERE name = '{name}' "
        if _type:
            path += f"WHERE type = '{_type}' "
        if balance:
            path += f"WHERE balance > {str(balance)} "
        if limit:
            path += f"LIMIT {str(limit)}"

        data = cls.format_data(cls.execute(path, cls.fetchall))

        if name:
            return data[0]
        return data

    @classmethod
    def load_with_balance(cls):
        path = f"SELECT * FROM {cls.table_name} WHERE balance > 0"

        data = cls.format_data(cls.execute(path, cls.fetchall))

        return data

    @classmethod
    def load_must_free(cls, limit=None, _type=None inn=None):
        path = f"SELECT b.*, coalesce (o.active_cnt, 0) as active_cnt FROM  " \
               f"(SELECT * FROM bots WHERE type = '{_type}' AND status = 'FREE' AND "+(f"'{inn}' = ANY(inns)" if inn else "inns is null")+") b " \
               f"LEFT JOIN " \
               f"(SELECT bot_name,COUNT(active) active_cnt FROM orders WHERE active=TRUE GROUP BY bot_name, active ) o " \
               f"ON b.name=o.bot_name " \
               f"ORDER BY active_cnt LIMIT {limit}"

        print(path)

        data = cls.execute(path, cls.fetchall)
        data = [d[:-1] for d in data]
        data = cls.format_data(data)

        return data

    @classmethod
    def format_data(cls, data):
        bots = []
        for d in data:
            bot = Bot(*d)
            bot.addresses = [address.replace(';', ',') for address in bot.addresses] if bot.addresses else []
            bots += [bot]

        if bots:
            return bots
        else:
            return False


if __name__ == '__main__':
    bots= Bots.load_must_free(31, 'WB', '381108544328')
    for bot in bots:
        print(bot)
