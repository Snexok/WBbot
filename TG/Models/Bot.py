from TG.Models.Model import Model

COLUMNS = ['id', 'name', 'addresses', 'number', 'username', 'type', 'inns']

class Bot(Model):
    def __init__(self, id='0', name='', addresses=[], number='', username='', type='', inns=[]):
        super().__init__()
        self.id = id
        self.name = name
        self.addresses = addresses
        self.number = number
        self.username = username
        self.type = type
        self.inns = inns

    def insert(self):
        path = "INSERT INTO bots (id, name, addresses) VALUES "
        path += f"((SELECT MAX(id)+1 FROM addresses), '{self.name}', ARRAY{str(self.addresses)})"
        Bot.execute(path)

    def update(self):
        print(self.changed)
        if self.changed:
            path = "UPDATE bots SET "
            path += "addresses= ARRAY[" + ",".join(
                "'" + a.replace(",", ";") + "'" for a in self.addresses) + "]::text[] "
            path += f"WHERE name='{str(self.name)}'"
            Bot.execute(path)

    def __str__(self):
        res = ""
        for i, col in enumerate(COLUMNS):
            res += col + " = " + str(getattr(self, col)) + "; "
        return res


class Bots(Model):

    @classmethod
    def load(cls, name=None, limit=None, _type=None):
        path = "SELECT * FROM bots "
        if name:
            path += f"WHERE name='{name}' "
        if _type:
            path += f"WHERE type='{_type}' "
        if limit:
            path += f"LIMIT {str(limit)}"
        data = cls.execute(path, cls.fetchall)
        data = cls.format_data(data)
        if name:
            return data[0]
        return data

    @classmethod
    def load_must_free(cls, limit=None, _type=None):
        path = f"SELECT b.*, coalesce (o.active_cnt, 0) as active_cnt FROM  " \
               f"(SELECT * FROM bots WHERE type = '{_type}') b " \
               f"LEFT JOIN " \
               f"(SELECT bot_name,COUNT(active) active_cnt FROM orders WHERE active=TRUE GROUP BY bot_name, active ) o " \
               f"ON b.name=o.bot_name " \
               f"ORDER BY active_cnt LIMIT {limit}"
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
    bots= Bots.load_must_free(6, 'WB')
    for bot in bots:
        print(bot)
