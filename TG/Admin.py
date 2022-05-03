import random

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from TG.CONSTS import STATES
from TG.Models.Addresses import Addresses, Address
from TG.Models.Bot import Bot as Bot_model
from TG.Models.Bot import Bots as Bots_model
from TG.Models.Orders import Orders, Order

from WB.Bot import Bot

import datetime
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
        number = Orders.get_number()

        # preprocessing
        data_for_bots = self.pre_run_doc(update, context)

        tg_bots = Bots_model.load(limit=len(data_for_bots))

        if type(tg_bots) is list:
            self.bots = [Bot(data=tg_bot) for tg_bot in tg_bots]
        else:
            tg_bot = tg_bots
            self.bots = [Bot(data=tg_bot)]

        reports = []
        for i, bot in enumerate(self.bots):
            # main process
            report = self.run_bot(bot, data_for_bots[i], number)

            update.message.reply_photo(open(reports[i]['qr_code'], 'rb'))
            print('Для подтверждения введите y, для отклонения оплаты введите n')
            while True:
                payed = input()
                if payed.lower() == 'y':
                    reports += [report]
                elif payed.lower() == 'n':
                    pass

        start_date = str(datetime.date.today())
        for report in reports:
            pup_address = Addresses.load(address=report['post_place'])
            order = Order(number=number, total_price=report['total_price'], services_price=150, prices=report['prices'],
                          quantities=report['quantities'], articles=report['articles'], pup_address=pup_address.address,
                          pup_tg_id=pup_address.tg_id, bot_name=report['bot_name'], bot_surname=report['bot_surname'],
                          start_date=start_date, pred_end_date='2020-12-20', active=False)
            order.insert()

        update.message.reply_text('Ваш заказ выполнен, до связи')

        return STATES['MAIN']

    def save_order_doc(self, id, document):
        file_path = "orders/" + id + ".xlsx"
        with open(file_path, 'wb') as f:
            document.download(out=f)
        df = pd.read_excel(file_path)

        return df

    def run_bot(self, bot, data_for_bot, number):
        """
        Принцип размещения операций:
        Делить операции на блоке, между которыми можно отправлять статусные сообщения
        """

        post_place = random.choice(bot.data.addresses)

        report = bot.buy(data_for_bot, post_place, number)

        report['post_place'] = post_place
        report['bot_name'] = bot.data.name
        report['bot_surname'] = bot.data.surname

        return report

    def pre_run_doc(self, update, context):
        id = str(update.effective_user.id)
        document = context.bot.get_file(update.message.document)

        df = self.save_order_doc(id, document)

        orders = [row.tolist() for i, row in df.iterrows()]

        additional_data = self.get_additional_data(orders)
        for i, a_data in enumerate(additional_data):
            orders[i] += [a_data]

        max_bots = max([order[3] for order in orders])
        data_for_bots = [[] for _ in range(max_bots)]

        for _, order in enumerate(orders):
            article, search_key, quantity, pvz_cnt, additional_data = order

            for i in range(max_bots):
                if pvz_cnt > 0:
                    data_for_bots[i] += [[article, search_key, quantity, additional_data]]
                pvz_cnt -= 1

        return data_for_bots

    @staticmethod
    def get_additional_data(orders):
        watch_bot = Bot(name="Watcher")

        articles = [order[0] for order in orders]
        additional_data = []
        for i, article in enumerate(articles):
            data = watch_bot.get_data_cart(article)
            additional_data += [data]

        return additional_data

    def check_not_added_pup_addresses(self):
        """
        Проверяет наличие адресов ПВЗ, не распределённых по ботам

        return states (ADMIN_ADDRESS_DISTRIBUTION | ADMIN)
        """
        all_not_added_addresses = Addresses.get_all_not_added()

        tg_bots = Bots_model.load()
        bots_name = [tg_bots[i].name for i in range(len(tg_bots))]

        if len(all_not_added_addresses) > 0:
            res_message = 'Список не распределённых адресов:\n\n' \
                          + self.join_to_lines([address.address for address in all_not_added_addresses]) \
                          + '\nСписок БОТОВ:\n\n' \
                          + self.join_to_lines(bots_name) \
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

            bot = Bots_model.load(name=name)
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
