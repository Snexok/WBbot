import os
import ujson


class Bot:

    @staticmethod
    def update(u_bot_data):
        path = "data/bots.json"
        if not os.path.isfile(path):
            f = open(path, "a")
            local_bots = [{'name': u_bot_data['name'], 'data': {}}]
        else:
            f = open(path, 'r')
            local_bots = ujson.load(f)
            f.close()
            f = open(path, "w")
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
