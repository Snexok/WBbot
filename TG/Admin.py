from ast import Add
import random

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from TG.CONSTS import STATES, BOTS_NAME
from TG.Models.Addresses_PG import Addresses, Address
from TG.Models.Bot import Bot as TGBot
from TG.Models.Bot import Bots as TGBots
from TG.Models.Orders import Orders

from WB.Bot import Bot as WBBot

import pandas as pd

USLUGI_PRICE = 150

class Admin:
    def __init__(self):
        pass

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
        self.run_by_doc(update, context)

        return STATES['MAIN']

    def check_not_added_pup_addresses(self):
        """
        Проверяет наличие адресов ПВЗ, не распределённых по ботам

        return states (ADMIN_ADDRESS_DISTRIBUTION | ADMIN)
        """
        all_not_added_addresses = Addresses.get_all_not_added()

        if len(all_not_added_addresses) > 0:
            res_message = 'Список не распределённых адресов:\n\n' \
                          + self.join_to_lines([address.address for address in all_not_added_addresses]) \
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

        for bot_data in bots_data_str:
            bot_data = bot_data.split('\n')

            name = bot_data[0]
            new_addresses = bot_data[1:]

            bot = TGBots.load(name=name)
            bot.append(addresses=new_addresses)
            print(bot.addresses, bot.name)
            bot.update()

            for address in new_addresses:
                address = Address().load(address=address)
                print(address)
                address.set(added_to_bot=True)
                address.update()

        update.message.reply_text("Все адреса добавлены в ботов")

        return STATES['ADMIN']

    def join_to_lines(self, joined_elems):
        return "".join(map(lambda x: x + '\n', joined_elems))

    def save_order_doc(self, id, document):
        file_path = "orders/" + id + ".xlsx"
        with open(file_path, 'wb') as f:
            document.download(out=f)
        df = pd.read_excel(file_path)

        return df

    def run_by_doc(self, update, context):
        """
        Принцип размещения операций:
        Делить операции на блоке, между которыми можно отправлять статусные сообщения
        """
        order_data, data_for_bots = self.pre_run_doc(update, context)

        self.bots = [WBBot(name=BOTS_NAME[i]) for i in range(len(data_for_bots))]

        orders = []
        report = []
        for i, bot in enumerate(self.bots):
            post_place = random.choice(TGBots.load(bot.name).addresses)
            report += bot.buy(data_for_bots[i], post_place, order_data['order_id'])
            address = Addresses().search_adress(post_place, Addresses().load())
            update.message.reply_photo(open(report[i]['qr_code'], 'rb'))
            additional_data = data_for_bots[i][3]
            order = {'price': additional_data['total_price'],
                     'uslugi_price': additional_data['total_quatities'] * USLUGI_PRICE,
                     'pup': {'address': post_place, 'tg_id': address['tg_id']},
                     'bot': {'name': bot['name'], 'surname': bot['surname']}}
            orders += [order]

        Orders.save(orders)

        update.message.reply_text('Ваш заказ выполнен, до связи')

    def get_additional_datas(self, articles, total_quatities):
        additional_datas = []
        watch_bot = WBBot(name="Watcher")
        for i, article in enumerate(articles):
            additional_data = watch_bot.get_data_cart(article)
            price = additional_data['price']
            additional_data['total_price'] = price * total_quatities[i]
            additional_datas += [additional_data]

        return additional_datas

    def pre_run_doc(self, update, context):
        order_data = {}

        id = str(update.effective_user.id)
        document = context.bot.get_file(update.message.document)
        df = self.save_order_doc(id, document)

        orders = [row.tolist() for i, row in df.iterrows()]

        articles = [order[0] for order in orders]

        total_quatities = [order[2] * order[3] for order in orders]

        additional_datas = self.get_additional_datas(articles, total_quatities)
        for i, a_data in enumerate(additional_datas):
            orders[i] += [a_data]

        max_bots = max([order[3] for order in orders])
        data_for_bots = [[] for _ in range(max_bots)]


        for _, order in enumerate(orders):
            print(order)
            print(order[5])

            if len(order) == 6:
                article, search_key, quantity, pvz_cnt, _, additional_data = order
            else:
                article, search_key, quantity, pvz_cnt, additional_data = order

            for i in range(max_bots):
                if pvz_cnt > 0:
                    data_for_bots[i] += [[article, search_key, quantity, additional_data]]
                pvz_cnt -= 1

        order_data['order_id'] = str(orders[0][4])
        order_data['total_quatities'] = total_quatities

        return order_data, data_for_bots