# Python Modules
import os
import json
import logging
import pandas as pd

# For telegram api
# pip install python-telegram-bot --upgrade
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    CallbackQueryHandler, TypeHandler, ConversationHandler

logger = logging.getLogger(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

MAIN, ORDER, PVZ = range(3)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет")


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def main_handler(update: Update, context: CallbackContext):
    msg = update.message.text.lower()
    if "заказ" in msg:
        keyboard = [[InlineKeyboardButton(name[:30], callback_data=name[:30])] for name in ['Файл', 'Чат']]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Файлом или через чат?', reply_markup=reply_markup)

        return ORDER
    
    return MAIN


def track_users_handler(update: Update, context: CallbackContext) -> None:
    """Store the user id of the incoming update, if any."""
    id = str(update.effective_user.id)
    if not os.path.isfile("users_data/" + id + ".json"):
        f = open("users_data/" + id + ".json", "a")
        f.write('{"id": ' + id + '}')
        f.close()

def order_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    print('query', query.data)

    return MAIN

def docs_handler(update: Update, context: CallbackContext):
    context.bot.get_file(update.message.document).download()
    id = str(update.effective_user.id)
    with open("users_data/" + id + "_order.xlsx", 'wb') as f:
        context.bot.get_file(update.message.document).download(out=f)
    df = pd.read_excel("users_data/" + id + "_order.xlsx")
    pvzs = []
    orders = []
    for index, row in df.iterrows():
        articul, search_key, quantity, pvz = row.tolist()
        orders += [row.tolist()]
        pvzs += [pvz]
    max_bots = max(pvzs)
    _bots = bot[:max_bots]
    data_for_bots = []
    for i in range(max_bots):
        articul, search_key, quantity, pvz = orders[i]
        if pvz!=0:
            data_for_bots += [articul, search_key, quantity]
        pvz-=1
    print(data_for_bots)
    for i, bot in enumerate(_bots):
        bot.open_browser()
        bot.open('https://www.wildberries.ru')
#         bot.login('9104499982')
        bot.buy(data_for_bots[i])
    update.message.reply_text('принял, понял')

def get_config():
    file = open("config/config.config").read()
    config = eval(file)
    return config


def main() -> None:
    config = get_config()
    updater = Updater(config['tokens']['telegram'])

    dispatcher = updater.dispatcher

    dispatcher.add_handler(TypeHandler(Update, track_users_handler), group=-1)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & ~Filters.command, main_handler)],
        states={
            MAIN: [
                MessageHandler(Filters.text & ~Filters.command, main_handler)
            ],
            ORDER: [
                CallbackQueryHandler(order_callback_handler)
            ],
            PVZ: [
                MessageHandler(Filters.text & ~Filters.command, main_handler)
            ],
        },
        fallbacks=[CommandHandler("start", start)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
