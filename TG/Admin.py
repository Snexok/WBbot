import asyncio
import random
import io


from TG.Models.Addresses import Addresses
from TG.Models.Admin import Admins as Admins_model
from TG.Models.Bot import Bots as Bots_model
from TG.Models.Orders import Order as Order_Model, Orders as Orders_Model

from WB.Bot import Bot

from  datetime import date, datetime, timedelta
import pandas as pd

USLUGI_PRICE = 150

TEST = False


class Admin:
    @staticmethod
    def is_admin(id):
        if id in Admins_model.get_ids():
            return True
        else:
            return False

    @staticmethod
    async def open_bot(bot_name):
        bot = Bot(name=bot_name)
        await asyncio.gather(asyncio.to_thread(bot.open_bot))

    @classmethod
    async def inside(cls, message, number):
        print('TEST='+'TRUE' if TEST else 'FALSE')
        print('T='+'T' if TEST else 'F')
        document = io.BytesIO()
        await message.document.download(destination_file=document)
        # preprocessing
        data_for_bots = cls.pre_run_doc(document)

        print(len(data_for_bots))

        tg_bots_data = Bots_model.load(limit=len(data_for_bots), _type="WB")

        bots = [Bot(data=tg_bot_data) for tg_bot_data in tg_bots_data]

        for bot in bots:
            bot.open_bot(manual=False)

        # main process
        run_bots = [asyncio.to_thread(cls.run_bot, bot, data_for_bots[i], number) for i, bot in enumerate(bots)]
        reports = await asyncio.gather(*run_bots)

        # for report in reports:
        #     await message.answer_photo(open(report['qr_code'], 'rb'))

        run_bots = [asyncio.to_thread(bot.expect_payment) for i, bot in enumerate(bots)]
        paid = await asyncio.gather(*run_bots)
        print(paid)

        # start_datetime = str(datetime.now())
        # for i, report in enumerate(reports):
        #     pup_address = Addresses.load(address=report['post_place'])[0]
        #     order = Order_Model(number=number, total_price=report['total_price'], services_price=150, prices=report['prices'],
        #                   quantities=report['quantities'], articles=report['articles'], pup_address=pup_address.address,
        #                   pup_tg_id=pup_address.tg_id, bot_name=report['bot_name'], bot_surname=report['bot_surname'],
        #                   start_date=start_datetime, pred_end_date=str(report['pred_end_date']), active=True, statuses=['payment' for _ in range(len(report['articles']))])
        #     order.insert()
        for i, report in enumerate(reports):
            if paid[i]['payment'] or TEST:
                print(paid[i]['datetime'])
                pup_address = Addresses.load(address=report['post_place'])[0]
                order = Order_Model(number=number, total_price=report['total_price'], services_price=150, prices=report['prices'],
                              quantities=report['quantities'], articles=report['articles'], pup_address=pup_address.address,
                              pup_tg_id=pup_address.tg_id, bot_name=report['bot_name'], bot_surname=report['bot_surname'],
                              start_date=paid[i]['datetime'], pred_end_date=report['pred_end_date'],
                              active=paid[i]['payment'] or TEST, statuses=['payment' for _ in range(len(report['articles']))])
                order.insert()

                await message.answer(f"Заказ бота {report['bot_name']} оплачен, время оплаты {paid[i]['datetime']}")

        await message.answer('Ваш заказ выполнен, до связи')


        for i, bot in enumerate(bots):
            # cls.wait_order_ended(bot, reports[i]['pred_end_date'], reports[i]['articles'], message)
            loop = asyncio.get_event_loop()
            print(reports[i]['post_place'])
            pup_address = Addresses.load(address=reports[i]['post_place'])[0]
            print(pup_address.address)
            loop.create_task(cls.wait_order_ended(bot, reports[i]['pred_end_date'], reports[i]['articles'], pup_address.address, number, message))

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

    @classmethod
    def pre_run_doc(cls, document):
        df = pd.read_excel(document)
        orders = [row.tolist() for i, row in df.iterrows()]

        additional_data = cls.get_additional_data(orders)
        for i, a_data in enumerate(additional_data):
            orders[i] += [a_data]

        # max_bots = max([order[3] for order in orders])
        max_bots = len(orders)
        data_for_bots = [[] for _ in range(max_bots)]

        for j, order in enumerate(orders):
            article, search_key, quantity, pvz_cnt, additional_data = order
            data_for_bots[j] += [[article, search_key, quantity, additional_data]]

            # for i in range(max_bots):
            #     if pvz_cnt > 0:
            #         data_for_bots[i] += [[article, search_key, quantity, additional_data]]
            #     pvz_cnt -= 1

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

    @classmethod
    def check_not_added_pup_addresses(cls):
        """
        Проверяет наличие адресов ПВЗ, не распределённых по ботам

        return states (ADMIN_ADDRESS_DISTRIBUTION | ADMIN)
        """
        all_not_added_addresses = Addresses.get_all_not_added()

        tg_bots = Bots_model.load()
        bots_name = [tg_bots[i].name for i in range(len(tg_bots))]
        if all_not_added_addresses:
            if len(all_not_added_addresses) > 0:
                res_message = 'Список не распределённых адресов:\n\n' +\
                               cls.join_to_lines([address.address for address in all_not_added_addresses]) +\
                               '\nСписок БОТОВ:\n\n' +\
                               cls.join_to_lines(bots_name) +\
                               '\nНапишите название бота и адреса для него в формате:\n\n' +\
                               '<Имя Первого бота>\n' +\
                               '<1 адрес>\n' +\
                               '<2 адрес>\n\n' +\
                               '<Имя Второго бота>\n' +\
                               '<1 адрес>\n' +\
                               '<2 адрес>'
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

    @classmethod
    async def wait_order_ended(cls, bot: Bot, pred_end_date, articles, address, order_number, message):
        start_datetime = datetime.now()
        rnd_time = timedelta(hours=random.randint(7, 14), minutes=random.randint(0, 60), seconds=random.randint(0, 60))
        end_datetime = pred_end_date + rnd_time

        time_to_end = (end_datetime - start_datetime).total_seconds()

        await asyncio.sleep(time_to_end)

        await bot.check_readiness(articles, address, order_number, message, cls.wait_order_ended)

    @classmethod
    async def check_order(cls, bot_name, message):
        bot = Bot(name=bot_name)
        orders = Orders_Model.load(bot_name=bot_name, active=True)
        # print(bot.data.name)
        # async def check_order(bot):
        #     bot.open_bot(manual=False)
        #     bot.open_delivery()
        bot.open_bot(manual=False)
        order = orders[0]
        await bot.check_readiness(order.articles, order.pup_address, order.number, message, cls.wait_order_ended)
        # for order in orders:
        #     await bot.check_readiness(order.articles, order.pup_address, order.number, message, cls.wait_order_ended)
        # await asyncio.gather(asyncio.to_thread(check_order(bot)))

