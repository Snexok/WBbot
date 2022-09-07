import asyncio
import random
from datetime import datetime, timedelta

from loguru import logger

from TG.Admin import Admin
from aiogram import Bot as TG_Bot

from TG.Models.Addresses import Addresses_Model
from TG.Models.BotEvents import BotsEvents_Model
from TG.Models.Bots import Bots_Model
from TG.Models.Delivery import Delivery_Model, Deliveries_Model
from WB.Bot import Bot

from configs import config

DEBUG = config['DEBUG']
TEST = config['TEST']


async def bot_buy(message, bot_event):
    orders_data = []

    all_current_bot_events = BotsEvents_Model.load(event="FOUND", bot_name=bot_event.bot_name)

    reports = []
    if len(all_current_bot_events) > 1:
        for bot_event_from_all in all_current_bot_events:
            reports += bot_event_from_all.data
            await message.answer(f"Выкупается сразу {len(all_current_bot_events)} события id = {bot_event_from_all.id}")
    else:
        reports += [all_current_bot_events[0].data]
        await message.edit_text(f"Выкуп:\n\n"
                                f"ID события {all_current_bot_events[0].id}")

    articles = sum([report["articles"] for report in reports], [])

    logger.info(all_current_bot_events[0])

    order_data = bot_event.data

    bot_name = bot_event.bot_name
    logger.info("Bot Name : ", bot_name)
    bot_data = Bots_Model.load(bot_name)

    bot_data.set(status="BUYS")
    bot_data.update()
    bot = Bot(data=bot_data)

    bot.open_bot(manual=False)
    try:
        bot_event.event = "CHOOSE_ADDRESS"

        addresses = bot.data.addresses
        post_place = random.choice(addresses if type(addresses) is list else [addresses])
        order_data['post_place'] = post_place

        number = Deliveries_Model.get_number()

        bot_event.event = "BUYS"

        run_bot = asyncio.to_thread(bot.buy, [order_data], post_place, number)
        buy_res = await asyncio.gather(run_bot)
        buy_res = buy_res[0]

        if buy_res is list:
            orders_data = buy_res
        elif orders_data is str:
            msg = orders_data

            await message.answer(msg)
            return False

        bot_event.event = "CHECK_DELIVERY"
        hours = random.randint(10, 16)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        bot_event.datetime_to_run = order_data['pred_end_date'] + timedelta(hours=hours, minutes=minutes, seconds=seconds)
        bot_event.wait = True
    except Exception as e:
        logger.info(e)
        bot_event.event += " FAIL"
        bot_event.end_datetime = datetime.now()
        bot_event.wait = False

    bot_event.update()

    if "FAIL" in bot_event.event:
        msg = '❌ Ошибка выкупа ❌\n\n' \
              f'ID заказа {bot_event.id}\n' \
              f'Бот {bot_event.bot_name}\n' \
              f'Артикул {" ".join(articles)}'
    else:
        if message:
            await message.answer_photo(open(order_data['qr_code'], 'rb'))

        if TEST:
            paid = {'payment': True, 'datetime': datetime.now()}
        else:
            run_bot = asyncio.to_thread(bot.expect_payment)
            paid = await asyncio.gather(run_bot)
            paid = paid[0]

        orders_data += [order_data]
        if paid['payment']:
            logger.info(paid['datetime'])
            pup_address = Addresses_Model.load(address=order_data['post_place'])
            delivery = Delivery_Model(number=number, total_price=order_data['total_price'], services_price=50,
                                   prices=order_data['prices'],
                                   quantities=order_data['quantities'], articles=order_data['articles'],
                                   pup_address=order_data['post_place'],
                                   pup_tg_id=pup_address.tg_id, bot_name=order_data['bot_name'],
                                   bot_surname=order_data['bot_username'],
                                   start_date=paid['datetime'], pred_end_date=order_data['pred_end_date'],
                                   active=paid['payment'] or TEST,
                                   statuses=['payment' for _ in range(len(order_data['articles']))], inn=order_data['inn'])
            delivery.insert()

            if message:
                await message.answer(f"✅ Оплачен заказ бота {order_data['bot_name']} ✅\n\n"
                                     f"Артикулы {order_data['articles']}\n\n"
                                     f"Адрес доставки {order_data['post_place']}\n\n"
                                     f"Время оплаты {paid['datetime']}")
        else:
            if message:
                await message.answer(
                    f"❌ НЕ оплачен заказ бота {order_data['bot_name']} с артикулами {order_data['articles']}")

        bot_event.event = "CHECK_DELIVERY"

        logger.info(f"{order_data['pred_end_date']} предварительная дата доставки заказа")
        days = 0
        end_datetime = get_work_time(days)
        bot_event.end_datetime = end_datetime

        bot_event.update()

        bot_data.set(status="HOLD")
        bot_data.update()

    return orders_data

def get_work_time(days=0):
    now_datetime = datetime.now()
    now_hour = now_datetime.time().hour

    res_datetime = 0
    hours = random.randint(1, 48)
    minutes = random.randint(1, 59)
    seconds = random.randint(1, 59)

    while abs(hours+now_hour)%24 < 8:
        hours = random.randint(1, 48)

    res_datetime = now_datetime + timedelta(hours=hours, minutes=minutes, seconds=seconds, days=days)

    return res_datetime