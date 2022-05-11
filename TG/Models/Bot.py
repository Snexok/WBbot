import asyncio
import threading

from TG.Models.Model import Model


class Bots(Model):

    @staticmethod
    def load(name=None, limit=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM bots "
        if name:
            path += "WHERE name='" + name + "' "
        if limit:
            path += "LIMIT " + str(limit)
        print(path)
        data = Bots.execute(path, callback)
        print(data)
        return Bots.format_data(data)

    @staticmethod
    def format_data(data):
        bots = []
        for d in data:
            bot = Bot()
            bot.id = d[0]
            bot.name = d[1]
            bot.addresses = [address.replace(';', ',') for address in d[2]]
            bot.number = d[3]
            bot.surname = d[4]
            bots += [bot]

        if bots:
            if len(bots) == 1:
                return bots[0]
            return bots
        else:
            return False


class Bot(Model):
    def __init__(self, id='0', name='', addresses=[], number='', surname=''):
        super().__init__()
        self.id = id
        self.name = name
        self.addresses = addresses
        self.number = number
        self.surname = surname

    def insert(self, data):
        path = "INSERT INTO bots (id, name, addresses) VALUES "
        path += "((SELECT MAX(id)+1 FROM addresses), '" + data.name + "', ARRAY" + str(data.addresses) + ")"
        Bot.execute(path)

    def update(self):
        print(self.changed)
        if self.changed:
            path = "UPDATE bots SET "
            path += "addresses= ARRAY[" + ",".join(
                "'" + a.replace(",", ";") + "'" for a in self.addresses) + "]::text[] "
            path += "WHERE name='" + str(self.name) + "'"
            Bot.execute(path)
