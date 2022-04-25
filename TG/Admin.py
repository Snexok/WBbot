import random

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from TG.CONSTS import STATES, BOTS_NAME
from TG.Models.Addresses import Addresses
from TG.Models.Bot import Bot as TGBot

from WB.Bot import Bot as WBBot

import pandas as pd


class Admin:
    def __init__(self):
        self.addresses = Addresses()
    def handler(self, update: Update, context: CallbackContext):
        id = str(update.effective_user.id)
        if id in ['794329884', '653703299']:
            msg = update.message.text.lower()
            if 'admin' in msg:
                reply_keyboard = [
                    ['проверить ботов'],
                    ['inside'],
                    ['Назад']
                ]
                markup = ReplyKeyboardMarkup(reply_keyboard)
                update.message.reply_text('Добро пожаловать, Лорд ' + update.effective_user.name, reply_markup=markup)
                return STATES['ADMIN']
            elif 'проверить ботов' in msg:
                res_message, state = self.check_not_added_pup_addresses()
                update.message.reply_text(res_message)
                return state
            elif "inside" in msg:
                update.message.reply_text('Я тебя понял, понял, кидай заказ')
                return STATES['INSIDE']
            elif "назад" in msg:
                reply_keyboard = [
                    ['Admin'],
                    ['ПВЗ']
                ]
                markup = ReplyKeyboardMarkup(reply_keyboard)
                update.message.reply_text('Я тебя понял, понял, кидай заказ', reply_markup=markup)
                return STATES['MAIN']
        else:
            update.message.reply_text('СоЖеЛеЮ, Ты Не $%...АдМиН...>>>')
            return STATES['MAIN']

    def inside_handler(self, update: Update, context: CallbackContext):
        self.run_by_doc(update, context, True)

        return STATES['MAIN']

    def check_not_added_pup_addresses(self):
        """
        Проверяет наличие адресов ПВЗ, не распределённых по ботам

        return states (ADMIN_ADDRESS_DISTRIBUTION | ADMIN)
        """
        local_addresses = self.addresses.load()
        all_not_added_addresses = list(filter(lambda x: x['added_to_bot'] == False, local_addresses))
        if len(all_not_added_addresses) > 0:
            res_message = 'Список не распределённых адресов:\n\n' \
                          + self.join_to_lines([address['address'] for address in all_not_added_addresses]) \
                          + '\nСписок БОТОВ:\n\n' \
                          + self.join_to_lines(BOTS_NAME) \
                          + '\nНапишите название бота и адреса для него в формате:\n\n' \
                          + '<Имя Первого бота>\n' \
                          + '<1 адрес>\n' \
                          + '<2 адрес>\n\n' \
                          + '<Имя Второго бота>\n' \
                          + '<1 адрес>\n' \
                          + '<2 адрес>\n\n'
            state = STATES['ADMIN_ADDRESS_DISTRIBUTION']
        else:
            res_message = "Все адреса распределены"
            state = STATES['ADMIN']

        return res_message, state

    def address_distribution_handler(self, update: Update, context: CallbackContext):
        msg = update.message.text
        bots_data_str = msg.split('\n\n')
        local_addresses = self.addresses.load()
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

            self.tg_bot.update(bot)
        self.addresses.update(local_addresses)
        update.message.reply_text("Все адреса добавлены в ботов")

        return STATES['ADMIN']

    def join_to_lines(self, joined_elems):
        return "".join(map(lambda x: x + '\n', joined_elems))

    def run_by_doc(self, update, context, inside=False):
        id = str(update.effective_user.id)

        file_path = "orders/" + id + ".xlsx"
        with open(file_path, 'wb') as f:
            context.bot.get_file(update.message.document).download(out=f)
        df = pd.read_excel(file_path)

        orders = [row.tolist() for i, row in df.iterrows()]

        articles = [order[0] for order in orders]
        watch_bot = WBBot(name="Watcher")
        for i, article in enumerate(articles):
            orders[i] += [watch_bot.get_data_cart(article)]

        max_bots = max([order[3] for order in orders])
        bots = [WBBot(name=BOTS_NAME[i]) for i in range(max_bots)]
        data_for_bots = [[] for _ in range(max_bots)]

        for _, order in enumerate(orders):
            if inside:
                article, search_key, quantity, pvz_cnt, _, additional_data = order
            else:
                article, search_key, quantity, pvz_cnt, additional_data = order

            for i in range(max_bots):
                if pvz_cnt > 0:
                    data_for_bots[i] += [[article, search_key, quantity, additional_data]]
                pvz_cnt -= 1


        order_id = str(orders[0][4])

        report = []
        for i, bot in enumerate(bots):
            post_places = random.choice(TGBot.load(bot.name)['data']['addresses'])
            report += bot.buy(data_for_bots[i], post_places, order_id)
            update.message.reply_photo(open(report[i]['qr_code'], 'rb'))

        update.message.reply_text('Ваш заказ выполнен, до связи')
