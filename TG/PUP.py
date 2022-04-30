from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from TG.CONSTS import STATES, PUP_STATES
from TG.Models.Addresses_PG import Addresses, Address
from TG.Models.Users import Users


class PUP:
    """Pick Up Point"""
    def __init__(self):
        pass

    def handler(self, update: Update, context: CallbackContext):
        msg = update.message.text
        _msg = msg.lower()
        id = str(update.effective_user.id)
        user = Users.load(id)
        pup_state = user.pup_state

        if _msg == 'всё':
            pup_state = PUP_STATES['END']

        if pup_state == PUP_STATES['FULL_NAME']:
            name = msg
            user.set(name=name)

            pup_state = PUP_STATES['ADRESSES']

            update.message.reply_text('Напишите адреса ваших ПВЗ')
        elif pup_state == PUP_STATES['ADRESSES']:
            new_addresses = [a for a in msg.splitlines()]

            user.append(addresses=new_addresses)

            for address in new_addresses:
                Addresses.insert(Address(address=address, tg_id=id))

            reply_keyboard = [
                ['Всё']
            ]
            markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
            addresses_to_print = "".join(map(lambda x: x + '\n', [address for address in user.addresses]))

            update.message.reply_text(
                'Это все адреса?\n\n' + addresses_to_print + '\nЕсли есть еще адреса напишите их?\n\nЕсли это все адреса, просто напишите "Всё"', reply_markup=markup)
        elif pup_state == PUP_STATES['END']:
            update.message.reply_text('Мы запомнили ваши данные')
            return STATES['MAIN']

        user.set(pup_state=pup_state)
        user.update()
