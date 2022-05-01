from TG.Models.Model import Model


class Bots(Model):

    @staticmethod
    def load(name=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM bots WHERE name='" + name + "'"
        return Bots().format_data(Bots().execute(path, callback))

    @staticmethod
    def format_data(data):
        bots = []
        for d in data:
            bot = Bot()
            bot.id = d[0]
            bot.name = d[1]
            bot.addresses = d[2]
            bot.number = d[3]
            bots += [bot]

        if bots:
            if len(bots):
                return bots[0]
            return bots
        else:
            return False


class Bot(Model):
    def __init__(self, id='0', name='', addresses=[], number=''):
        super().__init__()
        self.id = id
        self.name = name
        self.addresses = addresses
        self.number = number

    def insert(self, data):
        path = "INSERT INTO bots (id, name, addresses) VALUES "
        path += "((SELECT MAX(id)+1 FROM addresses), '" + data.name + "', ARRAY" + str(data.addresses) + ")"
        Bot.execute(path)

    def update(self):
        print(self.changed)
        if self.changed:
            path = "UPDATE bots SET "
            path += "addresses= ARRAY" + str(self.addresses) + "::text[] "
            path += "WHERE name='" + str(self.name) + "'"
            Bot().execute(path)
