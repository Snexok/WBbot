# Python Modules
import logging

# Consts
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

import TG.CONSTS.STATES as STATES

# For telegram api
from aiogram import Bot, Dispatcher, executor, types

from TG.Admin import Admin
from TG.Models.User import User
from TG.PUP import PUP
from configs import config

API_TOKEN = config['tokens']['telegram']
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logger = logging.getLogger(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
admin = Admin()
pup = PUP()

# States
class States(StatesGroup):
    ADMIN = State()  # Will be represented in storage as 'Form:name'
    age = State()  # Will be represented in storage as 'Form:age'
    gender = State()  # Will be represented in storage as 'Form:gender'

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """

    await message.reply("Привет")



@dp.message_handler(lambda message: message.text=='Admin')
async def set_admin(message: types.Message):
    id = str(message.chat.id)
    print('admin')
    if id in ['794329884', '653703299']:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("проверить ботов")
        markup.add("inside")

        # Set state
        await States.ADMIN.set()
        await message.answer('Добро пожаловать, Лорд ' + message.chat.full_name, reply_markup=markup)
    else:
        await message.answer('СоЖеЛеЮ, Ты Не $%...АдМиН...>>>')
        # return STATES['MAIN']

@dp.message_handler(state=States.ADMIN)
async def echo(message: types.Message):
        msg = message.text.lower()
        print(msg)
        if 'проверить ботов' in msg:
            # res_message, state = self.check_not_added_pup_addresses()
            # await message.answer(res_message)
            await message.answer('проверка ботов пока не доступна')
            # return state
        elif "inside" in msg:
            await message.answer('Я тебя понял, понял, кидай заказ')
            # return STATES['INSIDE']

@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
