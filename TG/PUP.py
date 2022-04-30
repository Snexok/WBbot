from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from TG.CONSTS import STATES, PUP_STATES
from TG.Models.Addresses_PG import Addresses
from TG.Models.User import User


class PUP:
    """Pick Up Point"""
    def __init__(self):
        pass

    def handler(self, update: Update, context: CallbackContext):
        msg = update.message.text
        _msg = msg.lower()
        id = str(update.effective_user.id)
        user = User.load(id)
        pup_state = user.get('pup_state')

        if not pup_state:
            pup_state = PUP_STATES['FULL_NAME']
        elif _msg == 'всё':
            pup_state = PUP_STATES['END']

        if pup_state == PUP_STATES['FULL_NAME']:
            user['name'] = msg
            pup_state = PUP_STATES['ADRESSES']
            update.message.reply_text('Напишите адреса ваших ПВЗ')
        elif pup_state == PUP_STATES['ADRESSES']:
            addresses = user.get('addresses')

            if not addresses:
                addresses = []

            addresses += [a for a in msg.splitlines()]
            user['addresses'] = addresses


            reply_keyboard = [
                ['Всё']
            ]
            markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
            addresses_to_print = "".join(map(lambda x: x + '\n', [address for address in addresses]))
            update.message.reply_text(
                'Это все адреса?\n\n' + addresses_to_print + '\nЕсли есть еще адреса напишите их?\n\nЕсли это все адреса, просто напишите "Всё"', reply_markup=markup)
        elif pup_state == PUP_STATES['END']:
            addresses = Address
            Addresses().save(user['addresses'], id, added_to_bot=False)
            update.message.reply_text('Мы запомнили ваши данные')
            return STATES['MAIN']

        user['pup_state'] = pup_state
        print(user)
        User.save(user)
