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
from TG.Models.Users import Users_Model
from WB.Bot import Bot

from configs import config

DEBUG = config['DEBUG']
TEST = config['TEST']


async def bot_buy(message, bot_event):
    bot_name = bot_event.bot_name

    logger.info(f"{bot_name} start")

    # получаем все данные заказов из событий в статусе FOUND
    bot_events = BotsEvents_Model.load(event=["FOUND", "PAYMENT"], bot_name=bot_name)

    orders_data = [bot_event_from_all.data for bot_event_from_all in bot_events]

    logger.info(bot_events)

    articles = sum([report["articles"] for report in orders_data], [])

    logger.info(f"{bot_name} {articles}")

    bot_data = Bots_Model.load(bot_name)

    bot_data.set(status="BUYS")
    bot_data.update()
    bot = Bot(data=bot_data)

    bot.open_bot(manual=False)
    try:
        for bot_event in bot_events:
            bot_event.event = "CHOOSE_ADDRESS"

        post_place = random.choice(bot.data.addresses)
        for order_data in orders_data:
            order_data['post_place'] = post_place

        number = Deliveries_Model.get_number()

        bot_event.event = "BUYS"

        run_bot = asyncio.to_thread(bot.buy, orders_data, post_place, number)
        buy_res = await asyncio.gather(run_bot)
        logger.info(buy_res)
        buy_res = buy_res[0]

        if type(buy_res) is list:
            orders_data = buy_res
        elif type(orders_data) is str:
            msg = orders_data
            return msg
    except Exception as e:
        logger.info(e)
        msg = ''
        for bot_event in bot_events:
            bot_event.event += " FAIL"
            bot_event.end_datetime = datetime.now()
            bot_event.wait = False
            msg = '❌ Ошибка выкупа ❌\n\n' \
                  f'ID заказа {bot_event.id}\n' \
                  f'Бот {bot_event.bot_name}\n' \
                  f'Артикул {" ".join(articles)}'
            bot_event.update()
        return msg

    if message:
        await message.answer_photo(open(orders_data[0]['qr_code'], 'rb'))
    for order_data in orders_data:
        if TEST:
            paid = {'payment': True, 'datetime': datetime.now()}
        else:
            run_bot = asyncio.to_thread(bot.expect_payment)
            paid = await asyncio.gather(run_bot)
            paid = paid[0]

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
            logger.info(f"{bot_event.bot_name} send notify to action owner")
            user_name = Users_Model.load(inn=order_data['inn']).name
            await message.answer(f"✅ Оплачен заказ бота {order_data['bot_name']} ✅\n\n"
                                 f"Клиент: {user_name}\n"
                                 f"Артикулы {' '.join(articles)}\n\n"
                                 f"Адрес доставки {order_data['post_place']}\n\n"
                                 f"Время оплаты {paid['datetime']}")
        else:
            error_msg = f"❌ НЕ оплачен заказ бота {order_data['bot_name']} с артикулами {order_data['articles']}"
            logger.info(f"{bot_event.bot_name}, {error_msg}")
            bot_event.event = "PAID_LOSE"
            await message.answer(error_msg)

    for bot_event in bot_events:
        bot_event.event = "CHECK_DELIVERY"
        hours = random.randint(10, 16)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        bot_event.datetime_to_run = orders_data[0]['pred_end_date'] + timedelta(hours=hours, minutes=minutes,
                                                                                seconds=seconds)
        logger.info(f"{orders_data[0]['pred_end_date']} предварительная дата доставки заказа")

        bot_event.wait = True
        bot_event.update()

    bot_data.set(status="HOLD")
    bot_data.update()
    logger.info(f"{bot_data.name} go to HOLD")

    return True

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
