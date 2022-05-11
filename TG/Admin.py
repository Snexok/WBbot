import asyncio
import random

from multiprocessing import Pool

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

    @staticmethod
    def run_bot(bot, data_for_bot, number):
        """
        Принцип размещения операций:
        Делить операции на блоке, между которыми можно отправлять статусные сообщения
        """

        addresses = bot.data.addresses
        post_place = random.choice(addresses if type(addresses) is list else [addresses])

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
    def a_pre_run_doc(id, document):
        # df = Admin.save_order_doc(id, document)
        df = pd.read_excel(document)
        orders = [row.tolist() for i, row in df.iterrows()]

        additional_data = Admin.get_additional_data(orders)
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

    @staticmethod
    def check_not_added_pup_addresses():
        """
        Проверяет наличие адресов ПВЗ, не распределённых по ботам

        return states (ADMIN_ADDRESS_DISTRIBUTION | ADMIN)
        """
        all_not_added_addresses = Addresses.get_all_not_added()

        tg_bots = Bots_model.load()
        bots_name = [tg_bots[i].name for i in range(len(tg_bots))]

        if len(all_not_added_addresses) > 0:
            res_message = 'Список не распределённых адресов:\n\n' \
                          + Admin.join_to_lines([address.address for address in all_not_added_addresses]) \
                          + '\nСписок БОТОВ:\n\n' \
                          + Admin.join_to_lines(bots_name) \
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

    @staticmethod
    def join_to_lines(joined_elems):
        return "".join(map(lambda x: x + '\n', joined_elems))

    @staticmethod
    def generate_secret_key():
        import secrets
        secret_key = secrets.token_urlsafe(64)

        return secret_key

    @staticmethod
    def wait_order_ended(bot: Bot, pred_end_date, articles, message):
        async def wait_until(dt):
            # sleep until the specified datetime
            now = datetime.datetime.now()

            time_to_end_day = (dt - now).total_seconds()
            time_to_open = datetime.timedelta(hours=random.randint(7,14), minutes=random.randint(0,60)).total_seconds()
            wait_time = time_to_end_day + time_to_open

            await asyncio.sleep(15)
            # await asyncio.sleep(wait_time)

        async def run_at(dt, coro):
            await wait_until(dt)
            return await coro

        loop = asyncio.get_event_loop()
        dt = datetime.datetime.fromisoformat(pred_end_date)
        loop.create_task(run_at(dt, bot.check_readiness(pred_end_date, articles, message)))
