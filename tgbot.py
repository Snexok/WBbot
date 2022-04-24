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

ADMIN, ADMIN_ADDRESS_DISTRIBUTION, MAIN, ORDER, PVZ, INSIDE, PUP = range(7)
BOTS_NAME = ['Oleg', 'Einstein', 'Boulevard Depo']

# PUP_STATES
FULL_NAME, ADRESSES, END = range(3)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет")


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def admin_handler(update: Update, context: CallbackContext):
    id = str(update.effective_user.id)
    if id in ['794329884', '653703299']:
        msg = update.message.text.lower()
        print(msg)
        if 'admin' in msg:
            update.message.reply_text('Добро пожаловать, Лорд ' + update.effective_user.name)
            return ADMIN
        elif 'проверить ботов' in msg:
            res_message, state = admin_check_not_added_pup_addresses()
            update.message.reply_text(res_message)
            return state
    else:
        update.message.reply_text('СоЖеЛеЮ, Ты Не $%...АдМиН...>>>')
        return MAIN

def admin_check_not_added_pup_addresses():
    """
    Проверяет наличие адресов ПВЗ, не распределённых по ботам

    return states (ADMIN_ADDRESS_DISTRIBUTION | ADMIN)
    """
    local_addresses = load_addresses()
    all_not_added_addresses = list(filter(lambda x: x['added_to_bot'] == False, local_addresses))
    if len(all_not_added_addresses) > 0:
        res_message = 'Список не распределённых адресов:\n\n' \
                      + join_to_lines([address['address'] for address in all_not_added_addresses])\
                      + '\nСписок БОТОВ:\n\n'\
                      + join_to_lines(BOTS_NAME)\
                      + '\nНапишите название бота и адреса для него в формате:\n\n'\
                      + '<Имя Первого бота>\n'\
                      + '<1 адрес>\n'\
                      + '<2 адрес>\n\n'\
                      + '<Имя Второго бота>\n'\
                      + '<1 адрес>\n'\
                      + '<2 адрес>\n\n'
        state = ADMIN_ADDRESS_DISTRIBUTION
    else:
        res_message = "Все адреса распределены"
        state = ADMIN

    return res_message, state

def admin_address_distribution_handler(update: Update, context: CallbackContext):
    msg = update.message.text
    bots_data_str = msg.split('\n\n')
    local_addresses = load_addresses()
    for bot_data in bots_data_str:
        bot = {}
        bot_data = bot_data.split('\n')
        bot['name'] = bot_data[0]
        bot['data'] = {}
        bot['data']['addresses'] = bot_data[1:]
        print(bot)
        print(local_addresses)
        for address in bot['data']['addresses']:
            i = [local_address['address'] for local_address in local_addresses].index(address)
            local_addresses[i]['added_to_bot'] = True

        update_bot(bot)
    update_addresses(local_addresses)
    update.message.reply_text("Все адреса добавлены в ботов")

    return ADMIN

def update_bot(u_bot_data):
    path = "data/bots.json"
    if not os.path.isfile(path):
        f = open(path, "a")
        local_bots = [{'name': u_bot_data['name'], 'data': {}}]
    else:
        f = open(path, 'r')
        local_bots = json.load(f)
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
                print("in bot",bot['name'],"to",key,"added", value)
    json.dump(local_bots, f)
    f.close()


def join_to_lines(joined_elems):
    return "".join(map(lambda x: x + '\n', joined_elems))


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
        addresses = user.get('addresses')

        if not addresses:
            addresses = []

        addresses += [a for a in msg.splitlines()]
        user['addresses'] = addresses
        addresses_to_print = "".join(map(lambda x: x + '\n', [address for address in addresses]))
        update.message.reply_text(
            'Это все адреса?\n\n' + addresses_to_print + '\nЕсли есть еще адреса напишите их?\n\nЕсли это все адреса, просто напишите "Всё"')
    elif pup_state == END:
        save_addresses(user['addresses'], id, added_to_bot=False)
        update.message.reply_text('Мы запомнили ваши данные')
        return MAIN

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

def update_addresses(addresses):
    path = "data/addresses.json"
    f = open(path, "w")
    json.dump(addresses, f)
    f.close()

def save_addresses(addresses, id, added_to_bot=False):
    local_addresses = load_addresses()
    for address in addresses:
        if len(list(filter(lambda x: x['tg_id'] == id and x['address'] == address,
                           local_addresses))) == 0:
            local_addresses += [{"address": address, "added_to_bot": added_to_bot, "tg_id": id}]
    path = "data/addresses.json"
    f = open(path, "w")
    json.dump(local_addresses, f)
    f.close()

def load_addresses():
    path = "data/addresses.json"
    if not os.path.isfile(path):
        f = open(path, "a")
        local_addresses = []
    else:
        f = open(path, 'r')
        local_addresses = json.load(f)
    f.close()
    return local_addresses


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
        entry_points=[MessageHandler(Filters.regex('Admin'), admin_handler),
                      MessageHandler(Filters.text & ~Filters.command, main_handler)],
        states={
            ADMIN: [
                MessageHandler(Filters.regex('Admin'), admin_handler),
                MessageHandler(Filters.text, admin_handler)
            ],
            MAIN: [
                MessageHandler(Filters.regex('Admin'), admin_handler),
                MessageHandler(Filters.text, main_handler)
            ],
            ORDER: [
                CallbackQueryHandler(order_callback_handler),
                MessageHandler(Filters.text, order_handler)
            ],
            PVZ: [
                MessageHandler(Filters.text, main_handler)
            ],
            INSIDE: [
                MessageHandler(Filters.document, inside_handler)
            ],
            PUP: [
                MessageHandler(Filters.text, pickup_point_handler)
            ],
            ADMIN_ADDRESS_DISTRIBUTION: [
                MessageHandler(Filters.text, admin_address_distribution_handler)
            ],

        },
        fallbacks=[CommandHandler("start", start)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
