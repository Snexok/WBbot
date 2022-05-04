# Python Modules
import datetime
import io
import logging

# Consts
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

# For telegram api
from aiogram import Bot, Dispatcher, executor, types

from TG.Admin import Admin
from TG.Models.Addresses import Addresses, Address
from TG.Models.Orders import Orders, Order
from TG.Models.Users import Users
from TG.Models.Bot import Bots as Bots_model
from TG.Models.Bot import Bot as Bot_model
from configs import config
from TG.CONSTS import PUP_STATES

API_TOKEN = config['tokens']['telegram']
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class States(StatesGroup):
    ADMIN = State()
    MAIN = State()
    WHITELIST = State()
    INSIDE = State()
    ADMIN_ADDRESS_DISTRIBUTION = State()
    PUP = State()
    ORDER = State()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    whitelist = ['794329884']
    if str(message.chat.id) in whitelist:
        await States.MAIN.set()
        await message.reply("Привет")
    else:
        await States.WHITELIST.set()



@dp.message_handler(state=States.WHITELIST)
async def echo(message: types.Message):
    pass


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


@dp.message_handler(lambda message: message.text == 'Admin')
async def set_admin(message: types.Message):
    id = str(message.chat.id)
    print('admin')
    if id in ['794329884', '653703299']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Проверить ботов")
        markup.add("inside")
        markup.add("Назад")

        # Set state
        await States.ADMIN.set()
        await message.answer('Добро пожаловать, Лорд ' + message.chat.full_name, reply_markup=markup)


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


@dp.message_handler(state=States.INSIDE, content_types=['document'])
async def inside_handler(message: types.Message):
    number = await Orders.get_number()
    print('inside')
    id = str(message.chat.id)
    document = io.BytesIO()
    await message.document.download(destination_file=document)
    print(document)
    # preprocessing
    data_for_bots = await Admin.a_pre_run_doc(id, document)

    tg_bots_data = await Bots_model.load(limit=len(data_for_bots))

    print(tg_bots_data)

    if type(tg_bots_data) is list:
        bots = [Bot_model(data=tg_bot_data) for tg_bot_data in tg_bots_data]
    else:
        tg_bot_data = tg_bots_data
        bots = [Bot_model(data=tg_bot_data)]

    # main process
    reports = []
    for i, bot in enumerate(bots):
        report = Admin.run_bot(bot, data_for_bots[i], number)

        await message.answer(open(report['qr_code'], 'rb'))
        reports += [report]

    start_date = str(datetime.date.today())
    for report in reports:
        pup_address = Addresses.load(address=report['post_place'])[0]
        order = Order(number=number, total_price=report['total_price'], services_price=150, prices=report['prices'],
                      quantities=report['quantities'], articles=report['articles'], pup_address=pup_address.address,
                      pup_tg_id=pup_address.tg_id, bot_name=report['bot_name'], bot_surname=report['bot_surname'],
                      start_date=start_date, pred_end_date='2020-12-20', active=False)
        order.insert()

    await message.answer('Ваш заказ выполнен, до связи')

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
    executor.start_polling(dp, skip_updates=True)
