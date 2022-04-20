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

MAIN, ORDER, PVZ, INSIDE, PUP = range(5)
BOTS_NAME = ['Oleg', 'Einstein', 'Boulevard Depo']

#PUP_STATES
FULL_NAME, ADRESSES, END = range(3)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет")


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def main_handler(update: Update, context: CallbackContext):
    # DEV
    id = str(update.effective_user.id)
    user = user_load(id)
    user['pup_state'] = 0
    user_save(user)
    # DEV

    msg = update.message.text.lower()
    if "пвз" in msg:
        update.message.reply_text("Ваше ФИО?")
        return PUP
    elif "заказ" in msg:
        keyboard = [[InlineKeyboardButton(name[:30], callback_data=name[:30])] for name in ['Файл', 'Чат']]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Файлом или через чат?', reply_markup=reply_markup)

        return ORDER
    elif "inside" in msg:
        update.message.reply_text('Я тебя понял, понял, кидай заказ')
        return INSIDE
    return MAIN


def pickup_point_handler(update: Update, context: CallbackContext):
    msg = update.message.text
    _msg = msg.lower()
    id = str(update.effective_user.id)
    user = user_load(id)
    pup_state = user.get('pup_state')

    if not pup_state:
        pup_state = FULL_NAME
    elif _msg == 'всё':
        pup_state = END

    if pup_state == FULL_NAME:
        user['name'] = msg
        pup_state = ADRESSES
        update.message.reply_text('Напишите адреса ваших ПВЗ')
    elif pup_state == ADRESSES:
        adresses = user.get('adresses')

        if not adresses:
            adresses = []

        adresses += msg.splitlines()
        user['adresses'] = adresses
        adresses_to_print = "".join(map(lambda x: x + '\n', adresses))
        update.message.reply_text('Это все адреса?\n\n'+adresses_to_print+'\nЕсли есть еще адреса напишите их?\n\nЕсли это все адреса, просто напишите "Всё"')
    elif pup_state == END:
        update.message.reply_text('Мы запомнили ваши данные')

    user['pup_state'] = pup_state
    print(user)
    user_save(user)

def track_users_handler(update: Update, context: CallbackContext) -> None:
    """Store the user id of the incoming update, if any."""
    id = str(update.effective_user.id)
    if not os.path.isfile("users_data/" + id + ".json"):
        f = open("users_data/" + id + ".json", "a")
        f.write('{"id": ' + id + '}')
        f.close()

def user_load(id):
    f = open("users_data/" + id + ".json", 'r')
    user = json.load(f)
    f.close()
    return user

def user_save(user):
    f = open("users_data/" + str(user['id']) + ".json", "w")
    json.dump(user, f)
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

    articles = [order[0] for order in orders]
    print(articles)
    watch_bot = Bot(name="Watcher")
    for i, article in enumerate(articles):
        orders[i] += [watch_bot.get_data_cart(article)]
    print(orders)

    max_bots = max([order[3] for order in orders])
    bots = [Bot(name=BOTS_NAME[i]) for i in range(max_bots)]
    data_for_bots = [[] for _ in range(max_bots)]

    for _, order in enumerate(orders):
        if inside:
            article, search_key, quantity, pvz_cnt, _, __, additional_data = order
        else:
            article, search_key, quantity, pvz_cnt, additional_data = order

        for i in range(max_bots):
            if pvz_cnt > 0:
                data_for_bots[i] += [[article, search_key, quantity, additional_data]]
            pvz_cnt -= 1

    post_places = [order[5] for order in orders][:max_bots]
    order_id = str(orders[0][4])

    report = []
    for i, bot in enumerate(bots):
        report += bot.buy(data_for_bots[i], post_places[i], order_id)
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
            PUP: [
                MessageHandler(Filters.text & ~Filters.command, pickup_point_handler)
            ]

        },
        fallbacks=[CommandHandler("start", start)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
