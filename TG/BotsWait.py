import asyncio
from asyncio import sleep
from aiogram import Bot

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
                self.exec_event()
                bots_wait.delete()

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
                await Admin.bot_search(self.data)
            elif self.event == 'BUY':
                await Admin.bot_buy()
            elif self.event == 'CHECK_DELIVERY':
                await Admin.check_order(self.data.bot_name)
            elif self.event == 'ADD_COMMENT':
                pass

