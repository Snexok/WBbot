# Python Modules
from datetime import datetime
import io
from random import random

import asyncio
import ujson
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

# For telegram api
from aiogram import Bot, Dispatcher, executor, types

from TG.Admin import Admin
from TG.Models.BotsWaits import BotsWait
from TG.Models.Addresses import Addresses, Address
from TG.Models.ExceptedOrders import ExceptedOrders, ExceptedOrder
from TG.Models.Orders import Orders
from TG.Models.Users import Users, User
from TG.Models.Bots import Bots as Bots_model
from TG.Models.Whitelist import Whitelist
from TG.Models.Admins import Admin as Admin_model
from TG.Markups import get_markup, get_keyboard, get_list_keyboard
from WB.Partner import Partner

from configs import config

import pandas as pd

DEBUG = True

ADMIN_BTNS = ['🏡 распределить адреса по ботам 🏡', '🔍 поиск товаров 🔎', '➕ добавить пользователя ➕', '◄ назад']

API_TOKEN = config['tokens']['telegram']
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# States
class States(StatesGroup):
    ADMIN = State()
    MAIN = State()
    WL_SECRET_KEY = State()
    INSIDE = State()
    ADMIN_ADDRESS_DISTRIBUTION = State()
    FF_ADDRESS_START = State()
    FF_ADDRESS_END = State()
    PUP_ADDRESSES_START = State()
    PUP_ADDRESSES_CONTINUE = State()
    ADMIN_ADDRESS_VERIFICATION = State()
    ORDER = State()
    TO_WL = State()
    REGISTER = State()
    RUN_BOT = State()
    CHECK_WAITS = State()
    BOT_SEARCH = State()
    BOT_BUY = State()
    COLLECT_OTHER_ORDERS = State()
    EXCEPTED_ORDERS_LIST = State()
    EXCEPTED_ORDERS_LIST_CHANGE = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    username = message.chat.username
    id = str(message.chat.id)
    print(username, id, 'is started')
    whitelisted = Whitelist.check(id)
    if whitelisted:
        await States.MAIN.set()
        is_admin = Admin.is_admin(id)
        if is_admin:
            markup = get_markup('main_main', is_admin=is_admin)
        else:
            user = Users.load(id)
            if user:
                markup = get_markup('main_main', user.role)
            else:
                markup = get_markup('main_main')
        await message.reply("Привет", reply_markup=markup)
    elif username:
        wl = Whitelist.set_tg_id(id, username=username)
        if wl:
            await States.MAIN.set()
            markup = get_markup('main_main')
            await message.reply("Привет", reply_markup=markup)
    else:
        await States.WL_SECRET_KEY.set()


@dp.message_handler(state=States.WL_SECRET_KEY)
async def whitelist_secret_key_handler(message: types.Message):
    secret_key = message.text
    id = str(message.chat.id)
    wl = Whitelist.set_tg_id(id, secret_key=secret_key)
    if wl:
        await States.MAIN.set()
        markup = get_markup('main_main')
        await message.answer("Привет", reply_markup=markup)


@dp.message_handler(lambda message: message.text == 'Admin')
async def set_admin(message: types.Message):
    id = str(message.chat.id)
    is_admin = Admin.is_admin(id)
    if is_admin:
        await States.ADMIN.set()
        markup = get_markup('admin_main', is_admin=is_admin, id=id)
        await message.answer(f'Добро пожаловать, Лорд {message.chat.full_name}', reply_markup=markup)


@dp.message_handler(state=States.MAIN)
async def main_handler(message: types.Message):
    msg = message.text.lower()
    if "⚡ регистрация ⚡" in msg:
        await States.REGISTER.set()
        markup = get_markup('main_register')
        await message.answer("Как вы хотите зарегистрировать:", reply_markup=markup)
    elif "🚀 собрать самовыкупы 🚀" in msg:
        # orders = Orders.load(collected=False)
        # for order in orders:
        #     await message.answer(f'Артикулы заказа {order.articles}\n\n'
        #                          f'Адрес заказа {order.pup_address}\n\n'
        #                          f'Время заказа {order.start_date}')
        # await message.answer('⛔ 🚀 Сборка самовыкупов пока не доступна 🚀 ⛔')
        await message.answer('Сборка началась')
        await Partner().collect_orders()
        await message.answer('Сборка закончилась')
    elif "⛔ собрать реальные заказы 🚚" in msg:
        await message.answer('⛔ Сборка РЕАЛЬНЫХ заказов ПОКА НЕДОСТУПНА ⛔')
        # users = Users.load(role='IE')
        # ies = [user.ie for user in users]
        # print(ies)
        # await States.COLLECT_OTHER_ORDERS.set()
        # markup = get_list_keyboard(ies)
        # await message.answer('Выберите ИП, по которому хотите собрать заказы', reply_markup=markup)
    elif "📑 список исключенных из сборки заказов 📑" in msg:
        # excepted_orders = ExceptedOrders.load()

        # excepted_orders_ie = []
        # for eo in excepted_orders:
        #     if eo.inn not in excepted_orders_ie:
        #         user = Users.load(inn=eo.inn)
        #         excepted_orders_ie += [user.ie]


        users = Users.load(role='IE')
        if users:
            ies = [user.ie for user in users]
            print(ies)
            await States.EXCEPTED_ORDERS_LIST.set()
            markup = get_list_keyboard(ies)
            await message.answer('Выберите ИП, по которому хотите посмотреть или изменить список', reply_markup=markup)
        else:
            await message.answer('Ни одно ИП не найдено')
    elif "заказ" in msg:
        await States.ORDER.set()
        markup = get_markup('main_order')
        await message.answer('Файлом или через чат?', reply_markup=markup)
    if "🌈 admin" in msg:
        await set_admin(message)


@dp.message_handler(state=States.REGISTER)
async def register_handler(message: types.Message):
    msg = message.text.lower()
    id = str(message.chat.id)

    if "как пвз" in msg:
        id = str(message.chat.id)
        user = Users.load(id)
        if not user:
            user = User(id, role='PUP')
            user.insert()

        await States.PUP_ADDRESSES_START.set()
    elif "как сотрудник фф" in msg:
        id = str(message.chat.id)
        user = Users.load(id)
        if not user:
            user = User(id, role='FF')
            user.insert()

        await States.FF_ADDRESS_START.set()
    elif "назад" in msg:
        await States.MAIN.set()
        markup = get_markup('main_main')
        await message.reply("Привет", reply_markup=markup)

    await message.answer("Ваше ФИО?")


@dp.message_handler(state=States.ADMIN)
async def admin_handler(message: types.Message):
    print(message)
    id = str(message.chat.id)
    msg = message.text.lower()
    print(msg)
    if '🏡 распределить адреса по ботам 🏡' in msg:
        res_message, state = Admin.check_not_added_pup_addresses()
        markup = get_markup('admin_main', id=id)
        await message.answer(res_message, reply_markup=markup)
        await getattr(States, state).set()
    elif '✉ проверить адреса ✉' in msg:
        res_message, state = Admin.check_not_checked_pup_addresses()
        markup = get_markup('admin_main', id=id)
        await message.answer(res_message, reply_markup=markup)
        await getattr(States, state).set()
    elif "🔍 поиск товаров 🔎" in msg:
        keyboard = get_keyboard('admin_bot_search')
        await message.answer('Пришлите Excel файл заказа\n'
                             'Или выберите артикул и выкупиться 1 товар с таким артикулом', reply_markup=keyboard)
        await States.BOT_SEARCH.set()
    elif "💰 выкуп собраных заказов 💰" in msg:
        bots_wait = BotsWait.load(event="FOUND")
        if bots_wait:
            await message.answer(f'{len(bots_wait)} ботов ожидают выкупа, скольких вы хотите выкупить?')
            await message.answer(
                '<b>ФИЧА</b>: <i>нажмите кнопку</i> <b>"💰 выкуп собраных заказов 💰"</b> <i>для того, чтобы выкупить</i> <b>только один</b>.',
                parse_mode="HTML")
            await States.BOT_BUY.set()
        else:
            markup = get_markup('admin_main', id=id)
            await message.answer('----------🎉Поздравляю!🎉--------\n'
                                 '💲Вы выкупили все заказы!💲', reply_markup=markup)
    elif "➕ добавить пользователя ➕" in msg:
        await States.TO_WL.set()
        markup = get_markup('admin_add_user')
        await message.answer('Выберите способ', reply_markup=markup)
    elif "◄ назад" in msg:
        await States.MAIN.set()
        is_admin = Admin.is_admin(id)
        if is_admin:
            markup = get_markup('main_main', is_admin=is_admin)
        else:
            markup = get_markup('main_main', Users.load(id).role)
        await message.answer('Главное меню', reply_markup=markup)
    elif "🕙 проверить ожидаемое 🕑" in msg:
        await States.CHECK_WAITS.set()

        orders = Orders.load(active=True, pred_end_date=datetime.now())
        bots_name = []
        for order in orders:
            if order.bot_name not in bots_name:
                bots_name += [order.bot_name]
        keyboard = get_keyboard('admin_bots', bots_name)
        await message.answer('Выберите бота', reply_markup=keyboard)
    else:
        if "🤖 открыть бота 🤖" in msg or "🤖 статус ботов 🤖" in msg:
            if id == '794329884' or id == '535533975':
                if "🤖 открыть бота 🤖" in msg:
                    await States.RUN_BOT.set()
                    tg_bots = Bots_model.load()
                    bots_name = [f"{tg_bots[i].name} {tg_bots[i].type}" for i in range(len(tg_bots))]
                    markup = get_keyboard('admin_bots', bots_name)
                    await message.answer('Выберите бота', reply_markup=markup)
                if "🤖 статус ботов 🤖":
                    pass
        else:
            await main_handler(message)


@dp.callback_query_handler(state=States.BOT_SEARCH)
async def bot_search_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data
    article = msg
    category = ''
    search_key = ''
    if article in ['90086267', '90086484', '90086527']:
        # category = 'Женщинам;Пляжная мода;Купальники'
        search_key = 'купальник женский раздельный с высокой талией'
    if article in '90085903':
        # category = 'Женщинам;Пляжная мода;Купальники'
        search_key = 'слитный купальник женский утягивающий'

    await States.ADMIN.set()

    orders = [[article, search_key, category, "1", "1", "381108544328"]]
    await call.message.edit_text(f'Начался поиск артикула {article}')

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
            await call.message.answer(f'Поиск артикула {article} упал на анализе карточки')

    if DEBUG:
        msgs = await Admin.bot_search(data_for_bots)
    else:
        try:
            msgs = await Admin.bot_search(data_for_bots)
        except:
            await call.message.answer(f'Поиск артикула {article} упал')
    try:
        for msg in msgs:
            res_msg += msg + "\n"
    except:
        pass

    res_msg += f'Поиск артикула {article} завершен'

    await call.message.answer(res_msg)


@dp.message_handler(state=States.BOT_SEARCH, content_types=['document'])
async def bot_search_handler(message: types.Message):
    await States.ADMIN.set()

    document = io.BytesIO()
    await message.document.download(destination_file=document)
    df = pd.read_excel(document)
    orders = [row.tolist() for i, row in df.iterrows()]
    data_for_bots = Admin.pre_run(orders)
    await message.answer('Поиск начался')
    if DEBUG:
        msgs = await Admin.bot_search(data_for_bots)
    else:
        try:
            msgs = await Admin.bot_search(data_for_bots)
        except:
            await message.answer('Поиск упал')

    for msg in msgs:
        await message.answer(msg)

    await message.answer('Поиск завершен')


@dp.message_handler(state=States.BOT_SEARCH, content_types=['text'])
async def inside_handler(message: types.Message):
    msg = message.text.lower()
    id = str(message.chat.id)
    if msg in ADMIN_BTNS:
        await States.ADMIN.set()
        if msg.lower() == '◄ назад':
            markup = get_markup('admin_main', id=id)
            await message.answer('Вы в меню Админа', reply_markup=markup)
        else:
            await admin_handler(message)
        return


@dp.callback_query_handler(state=States.RUN_BOT)
async def run_bot_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data
    bot_name, bot_type = msg.split(' ')
    await States.ADMIN.set()
    markup = get_markup('admin_main', id=id)
    await call.message.edit_text(msg + " открыт", reply_markup=markup)
    await Admin.open_bot(bot_name=bot_name)


@dp.message_handler(state=States.RUN_BOT)
async def run_bot_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text
    if msg.lower() in ADMIN_BTNS:
        await States.ADMIN.set()
        if msg.lower() == '◄ назад':
            markup = get_markup('admin_main', id=id)
            await message.answer('Вы в меню Админа', reply_markup=markup)
        else:
            await admin_handler(message)


@dp.callback_query_handler(state=States.CHECK_WAITS)
async def check_waits_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data
    await States.ADMIN.set()
    markup = get_markup('admin_main', id=id)
    await call.message.edit_text(msg + " открыт", reply_markup=markup)
    await Admin.check_order(msg, call.message)


@dp.message_handler(state=States.CHECK_WAITS)
async def check_waits_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text
    if msg.lower() in ADMIN_BTNS:
        await States.ADMIN.set()
        if msg.lower() == '◄ назад':
            markup = get_markup('admin_main', id=id)
            await message.answer('Вы в меню Админа', reply_markup=markup)
        else:
            await admin_handler(message)


@dp.callback_query_handler(state=States.COLLECT_OTHER_ORDERS)
async def run_bot_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    ie = call.data
    inn = Users.load(ie=ie).inn
    await States.MAIN.set()
    markup = get_markup('main_main', Users.load(id).role)

    await call.message.reply(f'Началась сборка РЕАЛЬНЫХ заказов {ie}', reply_markup=markup)

    await Partner().collect_other_orders(inn)

    await call.message.reply(f'Закончилась сборка РЕАЛЬНЫХ заказов  {ie}')


@dp.callback_query_handler(state=States.EXCEPTED_ORDERS_LIST)
async def run_bot_callback_query_handler(call: types.CallbackQuery, state: FSMContext):
    id = str(call.message.chat.id)
    ie = call.data
    inn = Users.load(ie=ie).inn
    excepted_orders = ExceptedOrders.load(inn=inn)
    await state.update_data(inn=inn)

    if excepted_orders:

        res_msg = f"Для клиента {ie} исключены заказы с номерами:"
        for eo in excepted_orders:
            res_msg += "\n" + eo.order_number
        res_msg += f"\n\nНапишите номера заказов,которые хотите изменить или добавить"
    else:
        res_msg = f"У клиента {ie} нет исключенных заказов"
        res_msg += f"\n\nНапишите номера заказов, которые хотите исключить"
    await States.EXCEPTED_ORDERS_LIST_CHANGE.set()
    await call.message.edit_text(res_msg)



@dp.message_handler(state=States.EXCEPTED_ORDERS_LIST_CHANGE)
async def run_bot_callback_query_handler(message: types.Message, state: FSMContext):
    msg = message.text
    id = str(message.chat.id)
    order_numbers = msg.replace("\n", " ").strip().split(" ")

    data = await state.get_data()
    inn = data['inn']
    excepted_orders = ExceptedOrders.load(inn=inn)

    if excepted_orders:

        local_order_numbers = [eo.order_number for eo in excepted_orders]

    added = []
    deleted = []
    for order_number in order_numbers:
        try:
            i = local_order_numbers.index(order_number)
            print(i)
            excepted_orders[i].delete()
            deleted += [order_number]
        except:
            eo = ExceptedOrder(inn=inn, order_number=order_number, start_datetime=datetime.now())
            eo.insert()
            added += [order_number]

    res_msg = ""
    if len(added):
        res_msg = f"Добавлены заказы:"
        for order_number in added:
            res_msg += "\n" + order_number

        if len(deleted):
            res_msg += "\n"
    if len(deleted):
        res_msg += "\n" + "Удалены заказы:"
        for order_number in deleted:
            res_msg += "\n" + order_number

    ie = Users.load(inn=inn).ie
    res_msg += "\n\n" + f"Для клиента {ie} исключены заказы с номерами:"
    excepted_orders = ExceptedOrders.load(inn=inn)

    for eo in excepted_orders:
        res_msg += "\n" + eo.order_number

    await States.MAIN.set()
    markup = get_markup('main_main', Users.load(id).role)
    await message.answer(res_msg, reply_markup=markup)


@dp.message_handler(state=States.TO_WL)
async def to_whitelist_handler(message: types.Message):
    msg = message.text.lower()
    id = str(message.chat.id)
    if msg in 'по username':
        await message.answer("Введите username пользователя")
    elif msg in 'сгененрировать ключ':
        secret_key = Admin.generate_secret_key()

        Whitelist(secret_key=secret_key).insert()

        await States.ADMIN.set()
        markup = get_markup('admin_main', id=id)
        await message.answer("Ключ для идентификации:")
        await message.answer(secret_key, reply_markup=markup)
    elif "@" in msg:
        username = msg[1:]
        Whitelist(username=username).insert()

        await States.ADMIN.set()
        markup = get_markup('admin_main', id=id)
        await message.answer(f"Пользователь с username {msg} добавлен", reply_markup=markup)
    elif msg in ADMIN_BTNS and Admin.is_admin(id):
        await States.ADMIN.set()
        if msg.lower() == '◄ назад':
            markup = get_markup('admin_main', id=id)
            await message.answer('Вы в меню Админа', reply_markup=markup)
        else:
            await admin_handler(message)
        return


@dp.message_handler(state=States.BOT_BUY, content_types=['text'])
async def bot_buy_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text
    if msg.lower() == "💰 выкуп собраных заказов 💰":
        bots_cnt = 1
    elif msg.lower() in ADMIN_BTNS:
        await States.ADMIN.set()
        if msg.lower() == '◄ назад':
            markup = get_markup('admin_main', id=id)
            await message.answer('Вы в меню Админа', reply_markup=markup)
        else:
            await admin_handler(message)
        return
    else:
        try:
            bots_cnt = int(msg)
        except:
            await message.answer('Вы указали не цифру, укажите цифру')
            return

    await States.ADMIN.set()

    await message.answer('Выкуп начался')

    await Admin.bot_buy(message, bots_cnt)

    await message.answer('Выкуп завершен')


@dp.message_handler(state=States.ADMIN_ADDRESS_DISTRIBUTION)
async def address_distribution_handler(message: types.Message):
    msg = message.text
    id = str(message.chat.id)
    if msg.lower() in ADMIN_BTNS:
        await States.ADMIN.set()
        if msg.lower() == '◄ назад':
            markup = get_markup('admin_main', id=id)
            await message.answer('Вы в меню Админа', reply_markup=markup)
        else:
            await admin_handler(message)
        return

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

    await States.ADMIN.set()
    markup = get_markup('admin_main', id=id)
    await message.answer('Все адреса добавлены в ботов', reply_markup=markup)


@dp.message_handler(state=States.FF_ADDRESS_START)
async def ff_address_start_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text

    user = Users.load(id)

    name = msg
    user.set(name=name)
    user.update()

    await States.FF_ADDRESS_END.set()
    await message.answer('Напишите адрес вашего ФФ')


@dp.message_handler(state=States.FF_ADDRESS_END)
async def ff_address_end_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text

    user = Users.load(id)

    address = msg
    user.append(addresses=[address])
    user.update()

    await States.MAIN.set()

    is_admin = Admin.is_admin(id)
    if is_admin:
        markup = get_markup('main_main', is_admin=is_admin)
    else:
        markup = get_markup('main_main', Users.load(id).role)
    await message.answer('Мы запомнили ваши данные', reply_markup=markup)


@dp.message_handler(state=States.ADMIN_ADDRESS_VERIFICATION)
async def address_verification_handler(message: types.Message):
    msg = message.text
    id = str(message.chat.id)

    if msg.lower() in ADMIN_BTNS:
        await States.ADMIN.set()
        if msg.lower() == '◄ назад':
            markup = get_markup('admin_main', id=id)
            await message.answer('Вы в меню Админа', reply_markup=markup)
        else:
            await admin_handler(message)
        return

    new_addresses = msg.split('\n')

    all_not_checked_addresses = Addresses.get_all_not_checked()

    for i, old_address_str in enumerate(all_not_checked_addresses):
        address = Address().load(address=old_address_str)
        address.append(address=new_addresses[i])
        address.update()

        user = Users.load(id=address.tg_id)
        for j, address in user.addresses:
            if address == old_address_str:
                user.addresses[j] = new_addresses[i]
                user.set(addresses=user.addresses)
                address.update()
                break

    await States.ADMIN.set()
    markup = get_markup('admin_main', Admin.is_admin(id), id)
    await message.answer('Все адреса обновлены', reply_markup=markup)


@dp.message_handler(state=States.PUP_ADDRESSES_START)
async def pup_addresses_start_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text

    user = Users.load(id)

    name = msg
    user.set(name=name)
    user.update()

    await States.PUP_ADDRESSES_CONTINUE.set()
    await message.answer('Напишите адреса ваших ПВЗ\n\n'
                         'Каждый адрес с новой строчки или каждый адрес в отдельном сообщении\n\n'
                         'Пример:\n'
                         'г Москва, Чистопрудная улица 32к2\n'
                         'г Москва, Вавиловская улица 22к8')


@dp.message_handler(state=States.PUP_ADDRESSES_CONTINUE)
async def pup_addresses_continue_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text

    user = Users.load(id)

    if msg.lower() == 'всё':
        await States.MAIN.set()

        is_admin = Admin.is_admin(id)
        if is_admin:
            markup = get_markup('main_main', is_admin=is_admin)
        else:
            markup = get_markup('main_main', Users.load(id).role)
        await message.answer('Мы запомнили ваши данные', reply_markup=markup)
    else:
        new_addresses = [a for a in msg.splitlines() if a]

        user.append(addresses=new_addresses)

        for address in new_addresses:
            Address(address=address, tg_id=id).insert()

        addresses_to_print = "".join(map(lambda x: x + '\n', [address for address in user.addresses]))

        markup = get_markup('pup_addresses')
        await message.answer(
            f'Это все адреса?\n\n{addresses_to_print}\nЕсли есть еще адреса напишите их?\n\nЕсли это все адреса, просто напишите "Всё"',
            reply_markup=markup)

    user.update()


@dp.message_handler()
async def default_handler(message: types.Message):
    username = message.chat.username
    id = str(message.chat.id)
    print(username, id, 'in default')
    whitelisted = Whitelist.check(id)
    if whitelisted:
        is_admin = Admin.is_admin(id)
        if is_admin:
            await States.ADMIN.set()
            await admin_handler(message)
        else:
            await States.MAIN.set()
            await main_handler(message)


if __name__ == '__main__':
    executor.start_polling(dp)
