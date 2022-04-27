import os

import ujson
import sys

from telegram import Update
from telegram.ext import CallbackContext

PATH = "data/orders.json"


class Orders:
    @staticmethod
    def load():
        with open(PATH, 'r') as f:
            orders = ujson.load(f)
        return orders

    @staticmethod
    def save(orders):
        _orders = Orders.load()
        if type(orders) is list:
            _orders += orders
        else:
            _orders += [orders]
        with open(PATH, "w") as f:
            ujson.dump(_orders, f)