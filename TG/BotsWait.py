import asyncio
from asyncio import sleep
from aiogram import Bot
from Bot import bot_search

from TG.Admin import Admin
from TG.Models.BotsWaits import BotWait_Model, BotsWait_Model


class BotsWait:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.event = ''
        self.data = None
        self.bot_name = ''
        self.sub_event = ''

    async def main(self):
        while True:
            await sleep(5)
            bots_wait = BotsWait_Model.load_last()
            print(bots_wait)
            if bots_wait:
                self.data = bots_wait.data
                self.bot_name = bots_wait.bot_name
                self.event = bots_wait.event
                self.sub_event = bots_wait.sub_event
                # Сбрасываем индикатор ожидания
                bots_wait.wait = False
                bots_wait.update()
                # Запускаем обработку события, все параметры передаются в self
                await self.exec_event()
                # bots_wait.delete()

    async def exec_event(self):
        if self.sub_event:
            if self.sub_event == 'SURF':
                pass
            elif self.sub_event == 'SEARCH_FAVORITES':
                pass
            elif self.sub_event == 'PICK_BASKET':
                pass
            elif self.sub_event == 'PICK_FAVORITE':
                pass
        else:
            if self.event == 'SEARCH':
                # Запуск процесса поиска
                data = self.data
                await bot_search(self.bot, data['chat_id'], data['article'], data['search_key'], data['category'])
            elif self.event == 'FOUND':
                # Уведомление о возможности выкупа
                data = self.data
                await Admin.send_notify_for_buy(self.bot, data['chat_id'], self.bot_name)
            elif self.event == 'CHECK_DELIVERY':
                # Проверка готовности товара
                await Admin.check_order(self.data.bot_name)
            elif self.event == 'ADD_COMMENT':
                pass

