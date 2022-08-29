import asyncio
import json
import random
from asyncio import sleep
from datetime import datetime, timedelta

import ujson
from aiogram import Bot as TG_Bot
from TG.Markups import get_keyboard

from configs import config
from TG.Admin import Admin
from TG.Models.Admins import Admins_Model, Admin_Model
from TG.Models.Bots import Bots_Model
from TG.Models.BotEvents import BotEvent_Model, BotsEvents_Model
from TG.Models.OrdersOfOrders import OrdersOfOrders_Model, OrderOfOrders_Model
from WB.Bot import Bot

DEBUG = config['DEBUG']


class BotEvents:
    def __init__(self, tg_bot: TG_Bot):
        self.tg_bot = tg_bot
        self.bot_event: BotEvent_Model = None

    async def main(self):
        while True:
            await sleep(5)
            bot_event = BotsEvents_Model.load_last()
            if bot_event:
                print(bot_event)
                self.bot_event = bot_event
                bot_event.running = True
                bot_event.update()
                # Запускаем обработку события, все параметры передаются в self
                #
                # loop = asyncio.get_event_loop()
                # loop.create_task(BotsWait(tg_bot).main())
                # loop.run_until_complete(do_io())
                # loop.run_until_complete(do_other_things())
                #
                # loop.close()
                # executor.start_polling(dp)
                await self.exec_event()
                # Сбрасываем индикатор ожидания
                bot_event.running = False
                bot_event.update()
                # bots_event.delete()

    async def exec_event(self):
        print(self.bot_event.event)
        if self.bot_event.sub_event:
            if self.bot_event.sub_event == 'SURF':
                pass
            elif self.bot_event.sub_event == 'SEARCH_FAVORITES':
                pass
            elif self.bot_event.sub_event == 'PICK_BASKET':
                pass
            elif self.bot_event.sub_event == 'PICK_FAVORITE':
                pass
        else:
            if self.bot_event.event == 'SEARCH':
                # Запуск процесса поиска
                data = self.bot_event.data

                admin: Admin_Model = Admins_Model.get_sentry_admin()

                msgs = []
                if DEBUG:
                    msgs = await self.bot_search(data['article'], data['search_key'], data.get('category'), data['inn'])
                else:
                    try:
                        msgs = await self.bot_search(data['article'], data['search_key'], data.get('category'),
                                                     data['inn'])
                    except:
                        await self.tg_bot.send_message(admin.id, f'❌ Поиск артикула {data["article"]} упал ❌')
                        return False

                res_msg = ''
                for msg in msgs:
                    res_msg += msg + "\n"

                res_msg += '\n' + f'Поиск артикула {data["article"]} завершен'

                await self.tg_bot.send_message(admin.id, res_msg)
                return True

            elif self.bot_event.event == 'FOUND':
                # Уведомление о возможности выкупа
                await self.send_notify_for_buy()
                return
            elif self.bot_event.event == 'CHECK_DELIVERY':
                # Проверка готовности товара
                status = await Admin.check_delivery(self.bot_wait.data.bot_name)

                if status:
                    self.bot_event.event = "CHECK_CLAIM"
                    self.bot_event.datetime_to_run = self.get_work_time()

                return
            elif self.bot_event.event == 'CHECK_BALANCE':
                await self.check_balance()
                return True
            elif self.bot_event.event == 'ADD_COMMENT':
                pass

    @classmethod
    def set_event_for_order(cls, order_id):
        order = OrdersOfOrders_Model.load(id=order_id)
        bots_event = BotsEvents_Model.load(order_id=order_id)

        bots_event_stat = {}
        for bot_event in bots_event:
            articles = bot_event.data.get('articles')
            print(articles)
            if articles:
                for article in articles:
                    if article in bots_event_stat:
                        bots_event_stat[article] += 1
                    else:
                        bots_event_stat[article] = 1
        print(bots_event_stat)
        order_stats = dict(zip(order.articles, order.quantities_to_bought))
        print(order_stats)
        for os_key, os_value in order_stats.items():
            article_cnt = bots_event_stat.get(os_key)
            if article_cnt:
                if article_cnt < os_value:
                    pass
                else:
                    print(os_key, article_cnt, os_value)
            else:
                pass

    @classmethod
    def get_work_time(cls, h=1, d=0):
        now_datetime = datetime.now()
        now_hour = now_datetime.time().hour

        res_datetime = 0
        hours = random.randint(h, h + 12)
        minutes = random.randint(1, 59)
        seconds = random.randint(1, 59)

        j = 0
        while abs(hours + now_hour) % 24 < 8:
            hours = random.randint(h + j, h + 12 + j)
            j += 2

        res_datetime = now_datetime + timedelta(hours=hours, minutes=minutes, seconds=seconds)
        return res_datetime

    @classmethod
    def BuildOrderFullfillmentProcess(cls, order: OrderOfOrders_Model):
        admin: Admin_Model = Admins_Model.get_sentry_admin()
        datas = []
        for i, article in enumerate(order.articles):
            for j in range(order.quantities_to_bought[i]):
                datas += [{'article': article, 'search_key': order.search_keys[i], 'inn': order.inn, 'chat_id':admin.id, }]

        # Перетасовываем заказы
        random.shuffle(datas)

        in_day_cnt = 0
        bonus_hours = 0
        for i, data in enumerate(datas):
            if in_day_cnt >= order.bought_per_day:
                bonus_hours += 24
                in_day_cnt = 0
            data = json.dumps(data)
            bw = BotEvent_Model(event="SEARCH", wait=True, datetime_to_run=cls.get_work_time(i + bonus_hours),
                                data=data)
            bw.insert()
            in_day_cnt += 1

    async def bot_search(self, article, search_key, category, inn):
        admin: Admin_Model = Admins_Model.get_sentry_admin()

        goods = [[article, search_key, category, "1", "1", inn]]
        await self.tg_bot.send_message(admin.id, f'Начался поиск артикула {article}')

        data_for_bots, status_fail = await Admin.get_data_of_goods(goods)
        if status_fail:
            await self.tg_bot.send_message(admin.id, f'❌ Поиск артикула {article} упал на анализе карточки ❌')

        if self.bot_event.bot_name:
            bot_data = Bots_Model.load(name=self.bot_wait.bot_name)
        else:
            bot_data = Bots_Model.load_must_free(limit=1, _type="WB")[0]
            self.bot_event.bot_name = bot_data.name
            self.bot_event.update()

        bot_data.set(status="SEARCH")
        bot_data.update()

        bot = Bot(data=bot_data)
        bot.open_bot(manual=False)

        run_bot = asyncio.to_thread(bot.search, data_for_bots[0])
        reports = await asyncio.gather(run_bot)
        report = reports[0]

        msgs = []
        print(report)
        datetime_to_run = self.get_work_time()

        if self.bot_event:
            self.bot_event.event = "FOUND"
            self.bot_event.wait = True
            self.bot_event.datetime_to_run = datetime_to_run
            print(self.bot_event.data)
            print(type(self.bot_event.data))
            # добавляем данные из поиска
            for key, value in report.items():
                self.bot_event.data[key] = value
            self.bot_event.data = ujson.dumps(self.bot_event.data)
            self.bot_event.update()
        else:
            bot_event = BotEvent_Model(bot_name=bot.data.name, event="FOUND", wait=True,
                                       start_datetime=datetime.now(), datetime_to_run=datetime_to_run,
                                       data=data)
            bot_event.insert()

        msgs += [f"✅ Собран заказ бота {report['bot_name']}✅\n"
                 f"Артикулы {report['articles']}\n"
                 f"Адреса: {bot_data.addresses}"]

        print("bot_search ended")

        del bot

        bot_data.status = "FOUND"
        bot_data.update()

        return msgs

    async def send_notify_for_buy(self):
        keyboard = get_keyboard('admin_notify_for_buy', self.bot_event.bot_name)
        await self.tg_bot.send_message(self.bot_event.data['chat_id'], 'Готов выкуп', reply_markup=keyboard)
        self.bot_event.event = "PAYMENT"
        self.bot_event.update()

    async def check_balance(self):
        bot = Bot(self.bot_event.bot_name)
        bot.open_bot(manual=False)
        balance = bot.check_balance()
        bot.data.balance = balance
        bot.data.update()
        if balance:
            self.bot_event.data = json.dumps({'balance': balance})


if __name__ == '__main__':
    # BotsWait.set_event_for_order('2')
    order = OrdersOfOrders_Model.load('куц')
    BotEvents.BuildOrderFulfillmentProcess(order)
