import asyncio
import random
from datetime import datetime, timedelta

from TG.Admin import Admin
from aiogram import Bot as TG_Bot

from TG.Models.Addresses import Addresses_Model
from TG.Models.Bots import Bots_Model
from TG.Models.Orders import Order_Model, Orders_Model
from WB.Bot import Bot

DEBUG = True
TEST = True


async def bot_search(tg_bot: TG_Bot, chat_id, article, search_key, category):
    orders = [[article, search_key, category, "1", "1", "381108544328"]]
    await tg_bot.send_message(chat_id, f'Начался поиск артикула {article}')

    res_msg = ''
    if DEBUG:
        run_bot = asyncio.to_thread(Admin.pre_run, orders)
        data_for_bots = await asyncio.gather(run_bot)
        data_for_bots = data_for_bots[0]
    else:
        try:
            run_bot = asyncio.to_thread(Admin.pre_run, orders)
            data_for_bots = await asyncio.gather(run_bot)
            data_for_bots = data_for_bots[0]
        except:
            await tg_bot.send_message(chat_id, f'❌ Поиск артикула {article} упал на анализе карточки ❌')

    if DEBUG:
        msgs = await Admin.bot_search(data_for_bots)
    else:
        try:
            msgs = await Admin.bot_search(data_for_bots)
        except:
            await tg_bot.send_message(chat_id, f'❌ Поиск артикула {article} упал ❌')
    try:
        for msg in msgs:
            res_msg += msg + "\n"
    except:
        pass

    res_msg += '\n' + f'Поиск артикула {article} завершен'

    tg_bot.send_message(chat_id, res_msg)


async def bot_buy(message, bot_wait):
    reports = []

    report = bot_wait.data

    bot_name = bot_wait.bot_name
    print("Bot Name : ", bot_name)
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

        bot_wait.event = "PAID"
    except Exception as e:
        print(e)
        bot_wait.event += " FAIL"

    bot_wait.end_datetime = datetime.now()
    bot_wait.wait = False
    bot_wait.data = []
    bot_wait.update()

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

        bot_wait.event = "CHECK_DELIVERY"

        print(report['pred_end_date'], 'предварительная дата доставки заказа\n', 'Если забудешь это поправить, это TG/Bot')
        days = 0
        end_datetime = get_work_time(days)
        bot_wait.end_datetime = end_datetime

        bot_wait.update()

        bot_data.set(status="FREE")
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