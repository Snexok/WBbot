import asyncio
import random
import io


from TG.Models.Addresses import Addresses
from TG.Models.Bot import Bots as Bots_model
from TG.Models.Orders import Order

from WB.Bot import Bot

import datetime
import pandas as pd

USLUGI_PRICE = 150

ADMIN_IDS = ['794329884', '653703299', '535533975', '791436094']


class Admin:
    @staticmethod
    def is_admin(id):
        if id in ADMIN_IDS:
            return True
        else:
            return False

    @staticmethod
    async def open_bot(bot_name):
        bot = Bot(name=bot_name)
        print(bot.data.name)
        await asyncio.gather(asyncio.to_thread(bot.open_bot))

    @staticmethod
    async def inside(message, number):
        document = io.BytesIO()
        await message.document.download(destination_file=document)
        # preprocessing
        data_for_bots = Admin.pre_run_doc(document)

        tg_bots_data = Bots_model.load(limit=len(data_for_bots))

        if type(tg_bots_data) is list:
            bots = [Bot(data=tg_bot_data) for tg_bot_data in tg_bots_data]
        else:
            tg_bot_data = tg_bots_data
            bots = [Bot(data=tg_bot_data)]

        # main process
        run_bots = [asyncio.to_thread(Admin.run_bot, bot, data_for_bots[i], number) for i, bot in enumerate(bots)]
        reports = await asyncio.gather(*run_bots)

        for report in reports:
            await message.answer_photo(open(report['qr_code'], 'rb'))

        start_date = str(datetime.date.today())
        for report in reports:
            print(report['pred_end_date'])
            pup_address = Addresses.load(address=report['post_place'])[0]
            order = Order(number=number, total_price=report['total_price'], services_price=150, prices=report['prices'],
                          quantities=report['quantities'], articles=report['articles'], pup_address=pup_address.address,
                          pup_tg_id=pup_address.tg_id, bot_name=report['bot_name'], bot_surname=report['bot_surname'],
                          start_date=start_date, pred_end_date=report['pred_end_date'], active=True)
            order.insert()

        await message.answer('Ваш заказ выполнен, до связи')


        for i, bot in enumerate(bots):
            # Admin.wait_order_ended(bot, reports[i]['pred_end_date'], reports[i]['articles'], message)
            Admin.wait_order_ended(bot, "2022-05-13", "reports[i]['articles']", message)

    @staticmethod
    def run_bot(bot: Bot, data_for_bot, number):
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

    @staticmethod
    def pre_run_doc(document):
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
        if all_not_added_addresses:
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
                state = 'ADMIN_ADDRESS_DISTRIBUTION'
            else:
                res_message = "Все адреса распределены"

                state = 'ADMIN'
        else:
            res_message = "Все адреса распределены"

            state = 'ADMIN'

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


