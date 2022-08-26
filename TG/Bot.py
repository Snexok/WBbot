import asyncio
import random
from datetime import datetime, timedelta

from TG.Admin import Admin
from aiogram import Bot as TG_Bot

from TG.Models.Addresses import Addresses_Model
from TG.Models.Bots import Bots_Model
from TG.Models.Orders import Order_Model, Orders_Model
from WB.Bot import Bot

from configs import config

DEBUG = config['DEBUG']
TEST = config['TEST']


async def bot_buy(message, bot_event):
    reports = []

    report = bot_event.data

    bot_name = bot_event.bot_name
    print("Bot Name : ", bot_name)
    bot_data = Bots_Model.load(bot_name)

    bot_data.set(status="BUYS")
    bot_data.update()
    bot = Bot(data=bot_data)

    bot.open_bot(manual=False)
    try:
        bot_event.event = "CHOOSE_ADDRESS"

        addresses = bot.data.addresses
        post_place = random.choice(addresses if type(addresses) is list else [addresses])
        report['post_place'] = post_place

        number = Orders_Model.get_number()

        bot_event.event = "BUYS"

        run_bot = asyncio.to_thread(bot.buy, report, post_place, number)
        reports = await asyncio.gather(run_bot)
        report = reports[0]

        bot_event.event = "CHECK_DELIVERY"
        hours = random.randint(10, 16)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        bot_event.datetime_to_run = report['pred_end_date'] + timedelta(hours=hours, minutes=minutes, seconds=seconds)
        bot_event.wait = True
    except Exception as e:
        print(e)
        bot_event.event += " FAIL"
        bot_event.end_datetime = datetime.now()
        bot_event.wait = False

    bot_event.update()

    if "FAIL" in bot_event.event:
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
            if message:
                await message.answer(
                    f"❌ НЕ оплачен заказ бота {report['bot_name']} с артикулами {report['articles']}")

        bot_event.event = "CHECK_DELIVERY"

        print(report['pred_end_date'], 'предварительная дата доставки заказа\n', 'Если забудешь это поправить, это TG/Bot')
        days = 0
        end_datetime = get_work_time(days)
        bot_event.end_datetime = end_datetime

        bot_event.update()

        bot_data.set(status="HOLD")
        bot_data.update()

    return reports

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