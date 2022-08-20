import asyncio
import random
from asyncio import sleep

import ujson

from aiogram import Bot as TG_Bot

from TG.Markups import get_markup, get_keyboard
from TG.Models.Addresses import Addresses_Model
from TG.Models.Admins import Admins_Model as Admins_Model
from TG.Models.Bots import Bots_Model as Bots_Model
from TG.Models.BotsWaits import BotWait_Model, BotsWait_Model
from TG.Models.Orders import Order_Model as Order_Model, Orders_Model as Orders_Model
from TG.States import States

from WB.Bot import Bot

from datetime import date, datetime, timedelta
import pandas as pd

USLUGI_PRICE = 50

TEST = False


class Admin:
    @staticmethod
    def is_admin(id):
        if id in Admins_Model.get_ids():
            return True
        else:
            return False

    @staticmethod
    async def open_bot(bot_name):
        bot = Bot(name=bot_name)
        await asyncio.gather(asyncio.to_thread(bot.open_bot))

    # @classmethod
    # async def inside(cls, message, number):
    #
    #
    #
    #     # for i, bot in enumerate(bots):
    #     #     # cls.wait_order_ended(bot, reports[i]['pred_end_date'], reports[i]['articles'], message)
    #     #     loop = asyncio.get_event_loop()
    #     #     print(reports[i]['post_place'])
    #     #     pup_address = Addresses.load(address=reports[i]['post_place'])[0]
    #     #     print(pup_address.address)
    #     #     loop.create_task(cls.wait_order_ended(bot, reports[i]['pred_end_date'], reports[i]['articles'], pup_address.address, number, message))

    @classmethod
    async def bot_search(cls, data):
        print("bot_search started")

        bots_data = Bots_Model.load_must_free(limit=len(data), _type="WB")

        for bot_data in bots_data:
            bot_data.set(status="SEARCH")
            bot_data.update()

        bots = [Bot(data=bot_data) for bot_data in bots_data]

        for bot in bots:
            bot.open_bot(manual=False)

        run_bots = [asyncio.to_thread(bot.search, data[i]) for i, bot in enumerate(bots)]
        reports = await asyncio.gather(*run_bots)

        msgs = []
        for i, report in enumerate(reports):
            print(report)
            data = ujson.dumps(report)
            end_datetime = cls.get_work_time()

            bot_wait = BotsWait_Model.load(bots[i].data.name, "SEARCH")
            if bot_wait:
                bot_wait.event = "FOUND"
                bot_wait.wait = True
                bot_wait.start_datetime = datetime.now()
                bot_wait.end_datetime = end_datetime
                # добавляем данные из поиска
                for key, value in data.items():
                    bot_wait.data[key] = value
                bot_wait.update()
            else:
                bot_wait = BotWait_Model(bot_name=bots[i].data.name, event="FOUND", wait=True,
                                         start_datetime=datetime.now(), end_datetime=end_datetime, data=data)
                bot_wait.insert()

            msgs += [f"✅ Собран заказ бота {report['bot_name']}✅\n"
                     f"Артикулы {report['articles']}"]

        print("bot_search ended")

        for bot in bots:
            del bot
        del bots

        for bot_data in bots_data:
            bot_data.status = "FOUND"
            bot_data.update()

        return msgs

    @classmethod
    async def bot_re_search(cls, bot_name, data):
        print("bot_search started")

        bot_data = Bots_Model.load(name=bot_name)

        bot_data.set(status="SEARCH")
        bot_data.update()

        bot = Bot(data=bot_data)

        bot.open_bot(manual=False)

        run_bots = asyncio.to_thread(bot.search, data[0])
        reports = await asyncio.gather(run_bots)

        msgs = []
        for i, report in enumerate(reports):
            print(report)
            data = ujson.dumps(report)
            bot_wait = BotWait_Model(bot_name=bot.data.name, event="RE_FOUND", wait=True,
                               start_datetime=datetime.now(), data=data)
            bot_wait.insert()

            msgs += [f"✅ Собран заказ бота {report['bot_name']}✅\n"
                     f"Артикулы {report['articles']}"]

        print("bot_search ended")


        del bot

        bot_data.set(status="RE_FOUND")
        bot_data.update()

        return msgs

    @staticmethod
    async def bot_buy(message=None, bots_cnt=1):
        bots_wait = BotsWait_Model.load(event="FOUND", limit=bots_cnt)

        reports = []

        for bot_wait in bots_wait:
            print(type(bot_wait.data))
            report = bot_wait.data
            # report = ujson.loads(bot_wait.data)

            bot_name = bot_wait.bot_name
            print("Bot Name _ ", bot_name)
            bot_data = Bots_Model.load(bot_name)

            bot_data.set(status="BUYS")
            bot_data.update()
            bot = Bot(data=bot_data)

            bot.open_bot(manual=False)
            try:
                bot_wait.event = "CHOOSE_ADDRESS"

                addresses = bot.data.addresses
                post_place = random.choice(addresses if type(addresses) is list else [addresses])
                report['post_place'] = post_place

                number = Orders_Model.get_number()

                bot_wait.event = "BUYS"

                run_bot = asyncio.to_thread(bot.buy, report, post_place, number)
                reports = await asyncio.gather(run_bot)
                report = reports[0]

            except Exception as e:
                print(e)
                bot_wait.event += " FAIL"

            if "FAIL" in bot_wait.event:
                if message:
                    await message.answer('❌ Ошибка выкупа ❌')
            else:
                if message:
                    await message.answer_photo(open(report['qr_code'], 'rb'))

                if TEST:
                    paid = {'payment': True, 'datetime': datetime.now()}
                else:
                    run_bot = asyncio.to_thread(bot.expect_payment)
                    paid = await asyncio.gather(run_bot)
                    paid = paid[0]

                reports += [report]
                if paid['payment']:
                    bot_wait.event = "PAID"
                    print(paid['datetime'])
                    pup_address = Addresses_Model.load(address=report['post_place'])
                    order = Order_Model(number=number, total_price=report['total_price'], services_price=50,
                                        prices=report['prices'],
                                        quantities=report['quantities'], articles=report['articles'],
                                        pup_address=report['post_place'],
                                        pup_tg_id=pup_address.tg_id, bot_name=report['bot_name'],
                                        bot_surname=report['bot_username'],
                                        start_date=paid['datetime'], pred_end_date=report['pred_end_date'],
                                        active=paid['payment'] or TEST,
                                        statuses=['payment' for _ in range(len(report['articles']))], inn=report['inn'])
                    order.insert()

                    if message:
                        await message.answer(f"✅ Оплачен заказ бота {report['bot_name']} ✅\n\n"
                                         f"Артикулы {report['articles']}\n\n"
                                         f"Адрес доставки {report['post_place']}\n\n"
                                         f"Время оплаты {paid['datetime']}")
                else:
                    bot_wait.event = "PAID_LOSE"
                    await message.answer(f"❌ НЕ оплачен заказ бота {report['bot_name']} с артикулами {report['articles']}")
                bot_wait.end_datetime = datetime.now()
                bot_wait.wait = False
                bot_wait.data = []
                bot_wait.update()

                bot_data.set(status="HOLD")
                bot_data.update()

        return reports\

    @staticmethod
    async def bot_re_buy(message, bot_wait):
        reports = []

        report = bot_wait.data
        # report = ujson.loads(bot_wait.data)

        bot_name = bot_wait.bot_name
        print("Bot Name _ ", bot_name)
        bot_data = Bots_model.load(bot_name)

        bot_data.set(status="BUYS")
        bot_data.update()
        bot = Bot(data=bot_data)

        bot.open_bot(manual=False)
        bot_wait.event = "CHOOSE_ADDRESS"

        addresses = bot.data.addresses
        post_place = random.choice(addresses if type(addresses) is list else [addresses])
        report['post_place'] = post_place

        number = Orders_Model.get_number()

        bot_wait.event = "BUYS"

        run_bot = asyncio.to_thread(bot.re_buy, report, post_place, number)
        reports = await asyncio.gather(run_bot)
        report = reports[0]

        bot_wait.event = "PAID"

        bot_wait.end_datetime = datetime.now()
        bot_wait.wait = False
        bot_wait.data = []
        bot_wait.update()

        if "FAIL" in bot_wait.event:
            await message.answer('❌ Ошибка выкупа ❌')
        else:
            reports += [report]
            if report['payment']:
                print(report['payment_datetime'])
                pup_address = Addresses.load(address=report['post_place'])
                order = Order_Model(number=number, total_price=report['total_price'], services_price=50,
                                    prices=report['prices'],
                                    quantities=report['quantities'], articles=report['articles'],
                                    pup_address=report['post_place'],
                                    pup_tg_id=pup_address.tg_id, bot_name=report['bot_name'],
                                    bot_surname=report['bot_username'],
                                    start_date=report['payment_datetime'], pred_end_date=report['pred_end_date'],
                                    active=report['payment'] or TEST,
                                    statuses=['payment' for _ in range(len(report['articles']))], inn=report['inn'])
                order.insert()

                await message.answer(f"✅ Оплачен заказ бота {report['bot_name']} ✅\n\n"
                                     f"Артикулы {report['articles']}\n\n"
                                     f"Адрес доставки {report['post_place']}\n\n"
                                     f"Время оплаты {report['payment_datetime']}")
            else:
                await message.answer(
                    f"❌ НЕ оплачен заказ бота {report['bot_name']} с артикулами {report['articles']}")

            bot_data.set(status="HOLD")
            bot_data.update()

        return reports

    @classmethod
    def pre_run(cls, orders):
        additional_data = cls.get_additional_data(orders)
        for i, a_data in enumerate(additional_data):
            orders[i] += [a_data]

        # max_bots = max([order[3] for order in orders])
        max_bots = len(orders)
        data_for_bots = [[] for _ in range(max_bots)]

        for j, order in enumerate(orders):
            article, search_key, category, quantity, pvz_cnt, inn, additional_data = order
            data_for_bots[j] += [
                {'article': article, 'search_key': search_key, 'category': category, 'quantity': quantity, 'inn': inn,
                 'additional_data': additional_data}]

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
        all_not_added_addresses = Addresses_Model.get_all_not_added()

        tg_bots = Bots_Model.load()
        bots_name = [tg_bots[i].name for i in range(len(tg_bots))]
        if all_not_added_addresses:
            if len(all_not_added_addresses) > 0:
                res_message = 'Список не распределённых адресов:\n\n' + \
                              cls.join_to_lines([address.address for address in all_not_added_addresses]) + \
                              '\nСписок БОТОВ:\n\n' + \
                              cls.join_to_lines(bots_name) + \
                              '\nНапишите название бота и адреса для него в формате:\n\n' + \
                              '<Имя Первого бота>\n' + \
                              '<1 адрес>\n' + \
                              '<2 адрес>\n\n' + \
                              '<Имя Второго бота>\n' + \
                              '<1 адрес>\n' + \
                              '<2 адрес>'
                state = 'ADMIN_ADDRESS_DISTRIBUTION'
            else:
                res_message = "Все адреса распределены"

                state = 'ADMIN'
        else:
            res_message = "Все адреса распределены"

            state = 'ADMIN'

        return res_message, state

    @classmethod
    def check_not_checked_pup_addresses(cls):
        """
        Проверяет наличие не проверенных адресов ПВЗ

        return states (ADMIN_ADDRESS_VERIFICATION | ADMIN)
        """
        all_not_checked_addresses = Addresses_Model.get_all_not_checked()

        if all_not_checked_addresses:
            if len(all_not_checked_addresses) > 0:
                res_message = 'Список не проверенных адресов:\n\n' + \
                              cls.join_to_lines([address.address for address in all_not_checked_addresses]) + \
                              '\nПопорядку напишите правильные адреса в формате:\n\n' + \
                              '<1 адрес>\n' + \
                              '<2 адрес>\n' + \
                              '<3 адрес>'
                state = 'ADMIN_ADDRESS_VERIFICATION'
            else:
                res_message = "Все адреса проверены"

                state = 'ADMIN'
        else:
            res_message = "Все адреса проверены"

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
    #
    # @classmethod
    # async def wait_order_ended(cls, bot: Bot, pred_end_date, articles, address, order_number, message):
    #     start_datetime = datetime.now()
    #     rnd_time = timedelta(hours=random.randint(7, 14), minutes=random.randint(0, 60), seconds=random.randint(0, 60))
    #     end_datetime = pred_end_date + rnd_time
    #
    #     time_to_end = (end_datetime - start_datetime).total_seconds()
    #
    #     await asyncio.sleep(time_to_end)
    #
    #     await bot.check_readiness(articles, address, order_number, message, cls.wait_order_ended)

    @classmethod
    async def check_order(cls, bot_name, message=None) -> bool:
        bot = Bot(name=bot_name)
        orders = Orders_Model.load(bot_name=bot_name, active=True, pred_end_date=datetime.now())
        bot.open_bot(manual=False)
        status: bool = await bot.check_readiness(orders, message)

        return status


        # await asyncio.gather(asyncio.to_thread(check_order(bot)))

    @classmethod
    def get_work_time(cls):
        now_datetime = datetime.now()
        now_hour = now_datetime.time().hour

        res_datetime = 0
        hours = random.randint(1, 48)
        minutes = random.randint(1, 59)
        seconds = random.randint(1, 59)

        while abs(hours+now_hour)%24 < 8:
            hours = random.randint(1, 48)

        res_datetime = now_datetime + timedelta(hours=hours, minutes=minutes, seconds=seconds)

        return res_datetime

if __name__ == '__main__':
    a = {"w": 2, "r": 3}
    b = {"t": 1}
    print(a, b)
    for key, value in a.items():
        b[key] = value
    print(b)