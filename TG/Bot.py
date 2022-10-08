import asyncio
import random
import time
from datetime import datetime, timedelta

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from TG.Admin import Admin
from aiogram import Bot as TG_Bot

from TG.Models.Addresses import Addresses_Model
from TG.Models.Admins import Admins_Model
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

    bot.open_bot()
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

        logger.info(type(buy_res))
        if type(buy_res) is list:
            logger.info(buy_res)
            orders_data = buy_res
        elif type(buy_res) is str:
            msg = buy_res
            return msg
    except Exception as e:
        logger.info("Выкуп упал")
        logger.info(e)
        return False

    if message:
        await message.answer_photo(open(orders_data[0]['qr_code'], 'rb'))
    if TEST:
        paid = {'payment': True, 'datetime': datetime.now()}
    else:
        run_bot = asyncio.to_thread(bot.expect_payment)
        paid = await asyncio.gather(run_bot)
        paid = paid[0]

    if paid['payment']:
        for order_data in orders_data:
            logger.info(paid['datetime'])
            logger.info(order_data)
            pup_address = Addresses_Model.load(address=order_data['post_place'])
            logger.info(pup_address)
            delivery = Delivery_Model(number=number, total_price=order_data['total_price'], services_price=50,
                                      prices=order_data['prices'],
                                      quantities=order_data['quantities'], articles=order_data['articles'],
                                      pup_address=order_data['post_place'],
                                      pup_tg_id=pup_address.tg_id, bot_name=order_data['bot_name'],
                                      bot_surname=order_data['bot_username'],
                                      start_date=paid['datetime'], pred_end_date=order_data['pred_end_date'],
                                      active=paid['payment'] or TEST,
                                      statuses=['payment' for _ in range(len(order_data['articles']))],
                                      inn=order_data['inn'])
            logger.info(delivery)
            delivery.insert()
            logger.info(f"{bot_event.bot_name} send notify to action owner")
            user_name = Users_Model.load(inn=order_data['inn']).name
            await message.answer(f"✅ Оплачен заказ бота {order_data['bot_name']} ✅\n\n"
                                 f"Клиент: {user_name}\n"
                                 f"Артикулы {' '.join(articles)}\n\n"
                                 f"Адрес доставки {order_data['post_place']}\n\n"
                                 f"Время оплаты {paid['datetime']}")
    else:
        error_msg = f"❌ НЕ оплачен заказ бота {bot_name}"
        logger.info(f"{bot_event.bot_name}, {error_msg}")
        bot_event.event = "PAID_LOSE"
        await message.answer(error_msg)
        return False

    for bot_event in bot_events:
        bot_event.event = "CHECK_DELIVERY"
        hours = random.randint(10, 16)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        bot_event.datetime_to_run = orders_data[0]['pred_end_date'] + timedelta(hours=hours, minutes=minutes,
                                                                                seconds=seconds)
        logger.info(f"{orders_data[0]['pred_end_date']} предварительная дата доставки заказа")

        bot_event.wait = True
        bot_event.running = False
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

    while abs(hours + now_hour) % 24 < 8:
        hours = random.randint(1, 48)

    res_datetime = now_datetime + timedelta(hours=hours, minutes=minutes, seconds=seconds, days=days)

    return res_datetime


async def check_delivery(bot_name):
    logger.info(f"{bot_name} started")

    bot = Bot(name=bot_name)
    deliveries = Deliveries_Model.load(bot_name=bot_name, active=True, pred_end_date=datetime.now())
    bot.open_bot()
    statuses = await bot.check_readiness_auto(deliveries)

    logger.info(f"{bot_name} ended")

    return any(statuses)


async def check_active_deliveries():
    deliveries = Deliveries_Model.load(active=True, pred_end_date=datetime.now())
    if deliveries:

        bots_name = []
        for delivery in deliveries:
            if delivery.bot_name not in bots_name:
                bots_name += [delivery.bot_name]

        # Запускаем проверку всех ботов с готовой доставкой
        for bot_name in bots_name:
            await check_delivery(bot_name)


async def check_all_found_events():
    bots_events = BotsEvents_Model.load(event=["FOUND", "PAYMENT"])
    bots_events.sort(key=lambda b_e: b_e.bot_name)
    bot_names = list(set([b_e.bot_name for b_e in bots_events]))
    _bots_events = [[b_e for b_e in bots_events if b_e.bot_name == bot_name] for bot_name in bot_names]
    for bot_events in _bots_events:
        if type(bot_events) is not list:
            bot_events = list(bot_events)

        bot_name = bot_events[0].bot_name
        bot = Bot(name=bot_name)

        logger.info(f"bot name = {bot_name}")

        run_bot = asyncio.to_thread(bot.check_basket, bot_events=bot_events)
        paid = await asyncio.gather(run_bot)
        paid = paid[0]





    # for b_e in bots_events:
    #     if b_e.bot_name not in bot_used:
    #         bot = Bot(name=b_e.bot_name)
    #         articles = []
    #         for i in range(len(bots_events)):
    #             if bots_events[i].bot_name == b_e.bot_name:
    #                 article = bots_events[i].data["article"]
    #
    #
    #         run_bot = asyncio.to_thread(bot.check_basket)
    #         paid = await asyncio.gather(run_bot)
    #         paid = paid[0]
    #
    #         bot_used += [b_e.bot_name]

async def save_article_img(article):
    run_bot = asyncio.to_thread(bot_save_article_img, article)
    await asyncio.gather(run_bot)

def bot_save_article_img(article):
    watch_bot = Bot(name="Watcher")

    watch_bot.driver.get("https://www.wildberries.ru/")
    time.sleep(2)
    watch_bot.driver.get(f"https://www.wildberries.ru/catalog/{str(article)}/detail.aspx?targetUrl=MI")
    time.sleep(2)

    cart_img = WebDriverWait(watch_bot.driver, 10).until(lambda d: d.find_element(By.XPATH, '//div[@class="zoom-image-container"]'))
    cart_img = cart_img.screenshot(f"cart_imgs/{article}.png")


if __name__ == '__main__':
    from configs import config

    API_TOKEN = config['tokens']['telegram']
    # Initialize bot and dispatcher
    tg_bot = TG_Bot(token=API_TOKEN)

    asyncio.run(check_all_found_events())
