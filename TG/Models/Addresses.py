import os

import ujson

PATH = "data/addresses.json"


class Addresses:

    @staticmethod
    def update(addresses):
        f = open(PATH, "w")
        ujson.dump(addresses, f)
        f.close()

    @staticmethod
    def save(addresses, id, added_to_bot=False):
        local_addresses = Addresses.load()
        for address in addresses:
            if len(list(filter(lambda x: x['tg_id'] == id and x['address'] == address,
                               local_addresses))) == 0:
                local_addresses += [{"address": address, "added_to_bot": added_to_bot, "tg_id": id}]
        f = open(PATH, "w")
        ujson.dump(local_addresses, f)
        f.close()

    @staticmethod
    def load():
        if not os.path.isfile(PATH):
            f = open(PATH, "a")
            local_addresses = []
        else:
            f = open(PATH, 'r')
            local_addresses = ujson.load(f)
        f.close()
        return local_addresses
