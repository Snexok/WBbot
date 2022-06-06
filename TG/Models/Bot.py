from TG.Models.Model import Model


class Bot(Model):
    def __init__(self, id='0', name='', addresses=[], number='', surname='', type='', inns=[]):
        super().__init__()
        self.id = id
        self.name = name
        self.addresses = addresses
        self.number = number
        self.surname = surname
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


class Bots(Model):

    @classmethod
    def load(cls, name=None, limit=None, _type=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM bots "
        if name:
            path += f"WHERE name='{name}' "
        if _type:
            path += f"WHERE type='{_type}' "
        if limit:
            path += f"LIMIT {str(limit)}"
        data = cls.execute(path, callback)
        data = cls.format_data(data)
        if name:
            return data[0]
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
