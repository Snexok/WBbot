# Python Modules
import asyncio
import datetime
import logging

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

# For telegram api
from aiogram import Bot, Dispatcher, executor, types

from TG.Admin import Admin
from TG.Models.Addresses import Addresses, Address
from TG.Models.Orders import Orders, Order
from TG.Models.Users import Users
from TG.Models.Bot import Bots as Bots_model
from TG.Models.Whitelist import Whitelist
from TG.Models.Admin import Admin as Admin_model

from WB.Bot import Bot as WB_Bot
from configs import config
from TG.CONSTS import PUP_STATES

DEBUG = False

API_TOKEN = config['tokens']['telegram']
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class States(StatesGroup):
    ADMIN = State()
    MAIN = State()
    WL_SECRET_KEY = State()
    INSIDE = State()
    ADMIN_ADDRESS_DISTRIBUTION = State()
    PUP = State()
    ORDER = State()
    TO_WL = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    username = message.chat.username
    id = str(message.chat.id)
    whitelisted = Whitelist.check(id)
    if whitelisted:
        await States.MAIN.set()
        await message.reply("Привет")
    elif username:
        wl = Whitelist.set_tg_id(id, username=username)
        if wl:
            await States.MAIN.set()
            await message.reply("Привет")
    else:
        await States.WL_SECRET_KEY.set()


@dp.message_handler(state=States.WL_SECRET_KEY)
async def whitelist_secret_key_handler(message: types.Message):
    secret_key = message.text
    id = str(message.chat.id)
    wl = Whitelist.set_tg_id(id, secret_key=secret_key)
    if wl:
        await States.MAIN.set()
        await message.answer("Привет")


@dp.message_handler(lambda message: message.text == 'Admin')
async def set_admin(message: types.Message):
    id = str(message.chat.id)
    if id in ['794329884', '653703299', '535533975']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Проверить ботов")
        markup.add("inside")
        markup.add("Добавить пользователя")
        markup.add("Назад")

        # Set state
        await States.ADMIN.set()
        await message.answer('Добро пожаловать, Лорд ' + message.chat.full_name, reply_markup=markup)


@dp.message_handler(state=States.MAIN)
async def main_handler(message: types.Message):
    msg = message.text.lower()
    if "пвз" in msg:
        id = str(message.chat.id)
        user = Users.load(id)
        user.set(pup_state=0)
        user.update()

        await message.answer("Ваше ФИО?")
        await States.PUP.set()
    elif "заказ" in msg:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Файл")
        markup.add("Чат")

        await message.answer('Файлом или через чат?', reply_markup=markup)

        await States.ORDER.set()
    if "admin" in msg:
        await set_admin(message)


@dp.message_handler(state=States.ADMIN)
async def admin_handler(message: types.Message):
    msg = message.text.lower()
    if 'проверить ботов' in msg:
        res_message, state = Admin.check_not_added_pup_addresses()
        await message.answer('проверка ботов пока не доступна')
        await message.answer(res_message)
        await getattr(States, state).set()
    elif "inside" in msg:
        await message.answer('Я тебя понял, понял, кидай заказ')
        await States.INSIDE.set()
    elif "добавить пользователя" in msg:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("По username")
        markup.add("Сгененрировать ключ")

        await message.answer('Выберите способ', reply_markup=markup)
        await States.TO_WL.set()
    elif "назад" in msg:
        await message.answer('Главное меню')
        await States.MAIN.set()


@dp.message_handler(state=States.TO_WL)
async def to_whitelist_handler(message: types.Message):
    msg = message.text.lower()
    if msg in 'по username':
        await message.answer("Введите username пользователя")
    elif msg in 'сгененрировать ключ':
        secret_key = Admin.generate_secret_key()

        Whitelist.set_secret_key(secret_key)

        await message.answer("Ключ для идентификации:")
        await message.answer(secret_key)
    elif "@" in msg:
        username = msg[1:]
        Whitelist.set_username(username)

        await message.answer("Пользователь с username " + msg + " добавлен")


@dp.message_handler(state=States.INSIDE, content_types=['document'])
async def inside_handler(message: types.Message):
    number = await Orders.get_number()

    await States.ADMIN.set()
    if DEBUG:
        await Admin.inside(message, number)
    else:
        try:
            await Admin.inside(message, number)
        except:
            admin = Admin_model().get_sentry_admin()
            await bot.send_message(admin.id, "Упал заказ номер " + str(number))

@dp.message_handler(state=States.INSIDE, content_types=['text'])
async def inside_handler(message: types.Message):
    msg = message.text.lower()
    if "назад" in msg:
        await message.answer('Я тебя понял, понял, кидай заказ')
        await States.MAIN.set()


@dp.message_handler(state=States.ADMIN_ADDRESS_DISTRIBUTION)
async def address_distribution_handler(message: types.Message):
    msg = message.text

    bots_data_str = msg.split('\n\n')

    for bot_data in bots_data_str:
        bot_data = bot_data.split('\n')

        name = bot_data[0]
        new_addresses = bot_data[1:]

        bot = Bots_model.load(name=name)
        bot.append(addresses=new_addresses)
        bot.update()

        for address in new_addresses:
            address = Address().load(address=address)
            address.set(added_to_bot=True)
            address.update()

    await message.answer('Все адреса добавлены в ботов')

    await States.ADMIN.set()


@dp.message_handler(state=States.PUP)
async def pup_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text.lower()

    user = Users.load(id)
    pup_state = user.pup_state

    if msg.lower() == 'всё':
        pup_state = PUP_STATES['END']

    if pup_state == PUP_STATES['FULL_NAME']:
        name = msg
        user.set(name=name)

        pup_state = PUP_STATES['ADRESSES']

        await message.answer('Напишите адреса ваших ПВЗ')

    elif pup_state == PUP_STATES['ADRESSES']:
        new_addresses = [a for a in msg.splitlines()]

        user.append(addresses=new_addresses)

        for address in new_addresses:
            Addresses.insert(Address(address=address, tg_id=id))

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Всё")

        addresses_to_print = "".join(map(lambda x: x + '\n', [address for address in user.addresses]))

        await message.answer(
            'Это все адреса?\n\n' + addresses_to_print + '\nЕсли есть еще адреса напишите их?\n\nЕсли это все адреса, просто напишите "Всё"',
            reply_markup=markup)

    user.set(pup_state=pup_state)
    user.update()

    if pup_state == PUP_STATES['END']:
        await message.answer('Мы запомнили ваши данные')
        await States.MAIN.set()


if __name__ == '__main__':
    executor.start_polling(dp)
    asyncio.to_thread()

