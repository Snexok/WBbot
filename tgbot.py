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

from Bot import Bot

logger = logging.getLogger(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

MAIN, ORDER, PVZ, INSIDE = range(4)
BOTS_NAME = ['Oleg', 'Einstein', 'Boulevard Depo']


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
    elif "inside" in msg:
        update.message.reply_text('Я тебя понял, понял, кидай заказ')
        return INSIDE
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
    answer = query.data
    if answer == "Файл":
        run_by_doc(update, context)
    elif answer == 'Чат':
        pass

    return MAIN


def inside_handler(update: Update, context: CallbackContext):
    run_by_doc(update, context, True)

    return MAIN


def run_by_doc(update, context, inside=False):
    id = str(update.effective_user.id)

    file_path = "users_data/" + id + "_order.xlsx"
    with open(file_path, 'wb') as f:
        context.bot.get_file(update.message.document).download(out=f)
    df = pd.read_excel(file_path)

    orders = [row.tolist() for i, row in df.iterrows()]

    max_bots = max([order[3] for order in orders])
    bots = [Bot(name=BOTS_NAME[i]) for i in range(max_bots)]
    data_for_bots = [[] for _ in range(max_bots)]

    for _, order in enumerate(orders):
        if inside:
            article, search_key, quantity, pvz_cnt, _, __ = order
        else:
            article, search_key, quantity, pvz_cnt = order

        for i in range(max_bots):
            if pvz_cnt > 0:
                data_for_bots[i] += [[article, search_key, quantity]]
            pvz_cnt -= 1
    print(data_for_bots)

    post_places = [order[5] for order in orders][:max_bots]
    order_id = str(orders[0][4])

    print(order_id, post_places)

    report = []
    for i, bot in enumerate(bots):
        report += bot.buy(data_for_bots[i], post_places[i], order_id)
        print(report[i]['qr_code'])
        update.message.reply_photo(open(report[i]['qr_code'], 'rb'))

    update.message.reply_text('Ваш заказ выполнен, до связи')


def get_config():
    file = open("config/config.config").read()
    config = eval(file)
    return config


def order_handler(args):
    pass


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
                CallbackQueryHandler(order_callback_handler),
                MessageHandler(Filters.text & ~Filters.command, order_handler)
            ],
            PVZ: [
                MessageHandler(Filters.text & ~Filters.command, main_handler)
            ],
            INSIDE: [
                MessageHandler(Filters.document, inside_handler)
            ],

        },
        fallbacks=[CommandHandler("start", start)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
