import asyncio
import random
from asyncio import sleep

import ujson

from aiogram import Bot as TG_Bot
from loguru import logger

from TG.Markups import get_markup, get_keyboard
from TG.Models.Addresses import Addresses_Model
from TG.Models.Admins import Admins_Model as Admins_Model
from TG.Models.Bots import Bots_Model as Bots_Model
from TG.Models.BotEvents import BotEvent_Model, BotsEvents_Model
from TG.Models.Delivery import Delivery_Model as Order_Model, Deliveries_Model as Orders_Model, Delivery_Model, \
    Deliveries_Model
from TG.Models.Users import Users_Model
from TG.Models.BotEvents import BotEvent_Model, BotsEvents_Model
from TG.Models.Delivery import Delivery_Model, Deliveries_Model
from TG.States import States

from WB.Bot import Bot

from datetime import date, datetime, timedelta
import pandas as pd

USLUGI_PRICE = 50

from configs import config

DEBUG = config['DEBUG']
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

    @classmethod
    async def bot_search(cls, data):
        logger.info("start")

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
            logger.info(report)
            data = ujson.dumps(report)
            end_datetime = cls.get_work_time()

            bot_event = BotsEvents_Model.load(bots[i].data.name, "SEARCH")
            if bot_event:
                bot_event = bot_event[0]
                bot_event.event = "FOUND"
                bot_event.wait = True
                bot_event.start_datetime = datetime.now()
                bot_event.end_datetime = end_datetime
                # добавляем данные из поиска
                for key, value in data.items():
                    bot_event.data[key] = value
                bot_event.update()
            else:
                bot_event = BotEvent_Model(bot_name=bots[i].data.name, event="FOUND", wait=True,
                                           start_datetime=datetime.now(), end_datetime=end_datetime, data=data)
                bot_event.insert()

            msgs += [f"✅ Собран заказ бота {report['bot_name']}✅\n"
                     f"Артикулы {report['articles']}"]


        for bot in bots:
            del bot
        del bots

        for bot_data in bots_data:
            bot_data.status = "FOUND"
            bot_data.update()

        logger.info("end")
        return msgs
    #
    # @classmethod
    # async def bot_re_search(cls, bot_name, data):
    #     logger.info("start")
    #
    #     bot_data = Bots_Model.load(name=bot_name)
    #
    #     bot_data.set(status="SEARCH")
    #     bot_data.update()
    #
    #     bot = Bot(data=bot_data)
    #
    #     bot.open_bot(manual=False)
    #
    #     run_bots = asyncio.to_thread(bot.search, data[0])
    #     reports = await asyncio.gather(run_bots)
    #
    #     msgs = []
    #     for i, report in enumerate(reports):
    #         logger.info(report)
    #         data = ujson.dumps(report)
    #         bot_event = BotEvent_Model(bot_name=bot.data.name, event="RE_FOUND", wait=True,
    #                                    start_datetime=datetime.now(), data=data)
    #         bot_event.insert()
    #
    #         msgs += [f"✅ Собран заказ бота {report['bot_name']}✅\n"
    #                  f"Артикулы {report['articles']}"]
    #
    #     logger.info("end")
    #
    #     del bot
    #
    #     bot_data.set(status="RE_FOUND")
    #     bot_data.update()
    #
    #     return msgs

    @staticmethod
    async def bot_buy(message, bots_cnt=1):
        bots_event = BotsEvents_Model.load(event="FOUND", limit=bots_cnt)

        for bot_event in bots_event:
            logger.info(f"{bot_event.bot_name} started")
            all_current_bot_events = BotsEvents_Model.load(event="FOUND", bot_name=bot_event.bot_name)

            bots_event_data = []
            if len(all_current_bot_events) > 1:
                for bot_event_from_all in all_current_bot_events:
                    bots_event_data += [bot_event_from_all.data]
                    # await message.answer(f"Выкупается сразу {len(all_current_bot_events)} события id = {bot_event_from_all.id}")
            else:
                bots_event_data += [all_current_bot_events[0].data]
                # await message.edit_text(f"Выкуп:\n\n"
                #                         f"ID события {all_current_bot_events[0].id}")

            logger.info(bots_event_data)

            articles = sum([[bot_event_data["article"]] for bot_event_data in bots_event_data], [])
            logger.info(articles)

            logger.info(all_current_bot_events[0])

            bot_name = bot_event.bot_name
            logger.info(f"Bot Name _ {bot_name}")
            bot_data = Bots_Model.load(bot_name)

            bot_data.set(status="BUYS")
            bot_data.update()
            bot = Bot(data=bot_data)

            bot.open_bot(manual=False)
            try:
                bot_event.event = "CHOOSE_ADDRESS"

                addresses = bot.data.addresses
                post_place = random.choice(addresses if type(addresses) is list else [addresses])
                for i in range(len(bots_event_data)):
                    bots_event_data[i]['post_place'] = post_place

                number = Deliveries_Model.get_number()

                bot_event.event = "BUYS"

                run_bot = asyncio.to_thread(bot.buy, bots_event_data, post_place, number)
                buy_res = await asyncio.gather(run_bot)
                logger.info(buy_res)
                buy_res = buy_res[0]

                if type(buy_res) is list:
                    logger.info(buy_res)
                    bots_event_data = buy_res
                elif type(buy_res) is str:
                    msg = buy_res
                    logger.info(msg)

                    await message.answer(msg)
                    continue

            except Exception as e:
                logger.info(e)
                bot_event.event += " FAIL"

            if "FAIL" in bot_event.event:
                msg = '❌ Ошибка выкупа ❌\n\n' \
                     f'ID заказа {bot_event.id}\n' \
                     f'Бот {bot_event.bot_name}\n' \
                     f'Артикул {" ".join(articles)}'

                await message.answer(msg)
            else:
                logger.info(bots_event_data)
                await message.answer_photo(open(bots_event_data[0]['qr_code'], 'rb'))
                for bot_event_data in bots_event_data:
                    if TEST:
                        paid = {'payment': True, 'datetime': datetime.now()}
                    else:
                        run_bot = asyncio.to_thread(bot.expect_payment)
                        paid = await asyncio.gather(run_bot)
                        paid = paid[0]

                    if paid['payment']:
                        bot_event.event = "PAID"
                        bot_event.end_datetime = datetime.now()
                        bot_event.wait = False
                        bot_event.data = []
                        bot_event.update()

                        logger.info(f"{bot_event.bot_name} create delivery")
                        pup_address = Addresses_Model.load(address=bot_event_data['post_place'])
                        delivery = Delivery_Model(number=number, total_price=bot_event_data['total_price'], services_price=50,
                                                  prices=bot_event_data['prices'],
                                                  quantities=bot_event_data['quantities'], articles=bot_event_data['articles'],
                                                  pup_address=bot_event_data['post_place'],
                                                  pup_tg_id=pup_address.tg_id, bot_name=bot_event_data['bot_name'],
                                                  bot_surname=bot_event_data['bot_username'],
                                                  start_date=paid['datetime'], pred_end_date=bot_event_data['pred_end_date'],
                                                  active=paid['payment'] or TEST,
                                                  statuses=['payment' for _ in range(len(bot_event_data['articles']))],
                                                  inn=bot_event_data['inn'])
                        delivery.insert()

                        logger.info(f"{bot_event.bot_name} send notify to action owner")
                        user_name = Users_Model.load(inn=bot_event_data['inn']).name
                        await message.answer(f"✅ Оплачен заказ бота {bot_event_data['bot_name']} ✅\n\n"
                                             f"Клиент: {user_name}\n"
                                             f"Артикулы {' '.join(articles)}\n\n"
                                             f"Адрес доставки {bot_event_data['post_place']}\n\n"
                                             f"Время оплаты {paid['datetime']}")
                    else:
                        error_msg = f"❌ НЕ оплачен заказ бота {bot_event_data['bot_name']} с артикулами {bot_event_data['articles']}"
                        logger.info(f"{bot_event.bot_name}, {error_msg}")
                        bot_event.event = "PAID_LOSE"
                        await message.answer(error_msg)

                    bot_data.set(status="HOLD")
                    bot_data.update()
                    logger.info(f"{bot_event.bot_name} go to HOLD")

    @staticmethod
    async def bot_re_buy(message, bot_event):
        reports = []

        report = bot_event.data
        # report = ujson.loads(bot_event.data)

        bot_name = bot_event.bot_name
        logger.info(f"Bot Name _ {bot_name}")
        bot_data = Bots_Model.load(bot_name)

        bot_data.set(status="BUYS")
        bot_data.update()
        bot = Bot(data=bot_data)

        bot.open_bot(manual=False)
        bot_event.event = "CHOOSE_ADDRESS"

        addresses = bot.data.addresses
        post_place = random.choice(addresses if type(addresses) is list else [addresses])
        report['post_place'] = post_place

        number = Deliveries_Model.get_number()

        bot_event.event = "BUYS"

        run_bot = asyncio.to_thread(bot.re_buy, report, post_place, number)
        reports = await asyncio.gather(run_bot)
        report = reports[0]

        bot_event.event = "PAID"

        bot_event.end_datetime = datetime.now()
        bot_event.wait = False
        bot_event.data = []
        bot_event.update()

        if "FAIL" in bot_event.event:
            await message.answer('❌ Ошибка выкупа ❌')
        else:
            reports += [report]
            if report['payment']:
                logger.info(report['payment_datetime'])
                pup_address = Addresses_Model.load(address=report['post_place'])
                delivery = Delivery_Model(number=number, total_price=report['total_price'], services_price=50,
                                          prices=report['prices'],
                                          quantities=report['quantities'], articles=report['articles'],
                                          pup_address=report['post_place'],
                                          pup_tg_id=pup_address.tg_id, bot_name=report['bot_name'],
                                          bot_surname=report['bot_username'],
                                          start_date=report['payment_datetime'], pred_end_date=report['pred_end_date'],
                                          active=report['payment'] or TEST,
                                          statuses=['payment' for _ in range(len(report['articles']))],
                                          inn=report['inn'])
                delivery.insert()

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
    def pre_run(cls, goods):
        additional_data = cls.get_additional_data(goods)
        for i, a_data in enumerate(additional_data):
            goods[i] += [a_data]

        # max_bots = max([order[3] for order in goods])
        max_bots = len(goods)
        data_for_bots = [[] for _ in range(max_bots)]

        for j, order in enumerate(goods):
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
    def get_additional_data(goods):
        watch_bot = Bot(name="Watcher")

        articles = [good[0] for good in goods]
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

    @classmethod
    async def check_delivery(cls, bot_name, message=None) -> bool:
        bot = Bot(name=bot_name)
        deliveries = Deliveries_Model.load(bot_name=bot_name, active=True, pred_end_date=datetime.now())
        bot.open_bot(manual=False)
        status: bool = await bot.check_readiness(deliveries, message)

        return status

    @classmethod
    def get_work_time(cls):
        now_datetime = datetime.now()
        now_hour = now_datetime.time().hour

        res_datetime = 0
        hours = random.randint(1, 48)
        minutes = random.randint(1, 59)
        seconds = random.randint(1, 59)

        while abs(hours + now_hour) % 24 < 8:
            hours = random.randint(1, 48)

        res_datetime = now_datetime + timedelta(hours=hours, minutes=minutes, seconds=seconds)

        return res_datetime

    @classmethod
    async def get_data_of_goods(cls, goods):
        data_for_bots = []
        status_fail = False
        if DEBUG:
            run_bot = asyncio.to_thread(cls.pre_run, goods)
            data_for_bots = await asyncio.gather(run_bot)
            data_for_bots = data_for_bots[0]
        else:
            try:
                run_bot = asyncio.to_thread(cls.pre_run, goods)
                data_for_bots = await asyncio.gather(run_bot)
                data_for_bots = data_for_bots[0]
            except:
                status_fail = True

        return data_for_bots, status_fail


if __name__ == '__main__':
    a = {"w": 2, "r": 3}
    b = {"t": 1}
    print(a, b)
    for key, value in a.items():
        b[key] = value
    print(b)
