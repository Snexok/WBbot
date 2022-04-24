import os

import ujson
import sys

from telegram import Update
from telegram.ext import CallbackContext

FOLDER = "users_data/"


class User:
    @staticmethod
    def load(id):
        f = open(FOLDER + id + ".json", 'r')
        user = ujson.load(f)
        f.close()
        return user

    @staticmethod
    def save(user):
        f = open(FOLDER + str(user['id']) + ".json", "w")
        ujson.dump(user, f)
        f.close()

    @staticmethod
    def track_handler(update: Update, context: CallbackContext) -> None:
        """Store the user id of the incoming update, if any."""
        id = str(update.effective_user.id)
        if not os.path.isfile(FOLDER + id + ".json"):
            f = open(FOLDER + id + ".json", "a")
            f.write('{"id": ' + id + '}')
            f.close()
