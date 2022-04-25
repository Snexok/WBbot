import os
import ujson

PATH = "data/bots.json"


class Bot:

    @staticmethod
    def update(u_bot_data):
        if not os.path.isfile(PATH):
            f = open(PATH, "a")
            local_bots = [{'name': u_bot_data['name'], 'data': {}}]
        else:
            local_bots = Bot.load()
            f = open(PATH, "w")
        local_bot_names = [bot['name'] for bot in local_bots]
        if u_bot_data['name'] in local_bot_names:
            i = local_bot_names.index(u_bot_data['name'])
            bot = local_bots[i]
        else:
            i = len(local_bots)
            bot = {'name': u_bot_data['name'], 'data': {}}
            local_bots += [bot]
        for key in u_bot_data['data']:
            if bot['data'].get(key) is None:
                bot['data'][key] = []
                local_bots[i]['data'][key] = []
            for value in u_bot_data['data'][key]:
                if not (value in bot['data'][key]):
                    local_bots[i]['data'][key] += [value]
                    print("in bot", bot['name'], "to", key, "added", value)
        ujson.dump(local_bots, f)
        f.close()

    @staticmethod
    def load(name=None):
        f = open(PATH, 'r')
        local_bots = ujson.load(f)
        f.close()
        if name:
            bot = next(filter(lambda b: b['name'] == name, local_bots))
            return bot
        else:
            return local_bots
