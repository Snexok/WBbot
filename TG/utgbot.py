# Python Modules
from datetime import datetime

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

# For telegram api
from aiogram import Bot, Dispatcher, executor, types

from TG.Admin import Admin
from TG.Models.BotsWaits import BotsWait
from TG.Models.Addresses import Addresses, Address
from TG.Models.Orders import Orders
from TG.Models.Users import Users, User
from TG.Models.Bot import Bots as Bots_model
from TG.Models.Whitelist import Whitelist
from TG.Models.Admin import Admin as Admin_model
from TG.Markups import get_markup, get_keyboard
from WB.Partner import Partner

from configs import config

DEBUG = True

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
            markup = get_markup('main_main', Users.load(id).role)
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
    if "регистрация" in msg:
        await States.REGISTER.set()
        markup = get_markup('main_register')
        await message.answer("Как вы хотите зарегистрировать:", reply_markup=markup)
    elif "собрать выкупы" in msg:
        await message.answer('Сборка началась')
        Partner().collect_orders()
        await message.answer('Сборка закончилась')
    elif "собрать реальные заказы" in msg:
        await message.answer('Сборка РЕАЛЬНЫХ заказов началась')

        await message.answer('Сборка РЕАЛЬНЫХ заказов закончилась')
    elif "заказ" in msg:
        await States.ORDER.set()
        markup = get_markup('main_order')
        await message.answer('Файлом или через чат?', reply_markup=markup)
    if "admin" in msg:
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
    elif "как фф" in msg:
        id = str(message.chat.id)
        user = Users.load(id)
        if not user:
            user = User(id, role='FF')
            user.insert()

        await States.FF_ADDRESS_START.set()

    await message.answer("Ваше ФИО?")


@dp.message_handler(state=States.ADMIN)
async def admin_handler(message: types.Message):
    print(message)
    id = str(message.chat.id)
    msg = message.text.lower()
    print(msg)
    if 'проверить ботов' in msg:
        res_message, state = Admin.check_not_added_pup_addresses()
        await message.answer(res_message)
        await getattr(States, state).set()
    elif 'проверить адреса' in msg:
        res_message, state = Admin.check_not_checked_pup_addresses()
        await message.answer(res_message)
        await getattr(States, state).set()
    elif "сделать выкуп" in msg:
        await message.answer('Пришлите Excel файл заказа')
        await message.answer('Или напишите артикул, сколько штук, на сколько ПВЗ')
        await States.INSIDE.set()
    elif "добавить пользователя" in msg:
        await States.TO_WL.set()
        markup = get_markup('admin_add_user')
        await message.answer('Выберите способ', reply_markup=markup)
    elif "назад" in msg:
        await States.MAIN.set()
        is_admin = Admin.is_admin(id)
        if is_admin:
            markup = get_markup('main_main', is_admin=is_admin)
        else:
            markup = get_markup('main_main', Users.load(id).role)
        await message.answer('Главное меню', reply_markup=markup)
    elif "проверить ожидаемое" in msg:
        print("проверить ожидаемое")
        await States.CHECK_WAITS.set()

        orders = Orders.load(active=True, pred_end_date=datetime.now())
        bots_name = []
        for order in orders:
            if order.bot_name not in bots_name:
                bots_name += [order.bot_name]
        keyboard = get_keyboard('admin_bots', bots_name)
        await message.answer('Выберите бота', reply_markup=keyboard)
    elif id == '794329884' or id == '535533975':
        if "открыть бота" in msg:
            await States.RUN_BOT.set()
            tg_bots = Bots_model.load()
            bots_name = [f"{tg_bots[i].name} {tg_bots[i].type}" for i in range(len(tg_bots))]
            markup = get_keyboard('admin_bots', bots_name)
            await message.answer('Выберите бота', reply_markup=markup)


@dp.callback_query_handler(state=States.RUN_BOT)
async def run_bot_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data
    bot_name, bot_type = msg.split(' ')
    await States.ADMIN.set()
    markup = get_markup('admin_main', id=id)
    await call.message.answer(msg + " открыт", reply_markup=markup)
    await Admin.open_bot(bot_name=bot_name)


@dp.callback_query_handler(state=States.CHECK_WAITS)
async def check_waits_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data
    await States.ADMIN.set()
    markup = get_markup('admin_main', id=id)
    await call.message.answer(msg + " открыт", reply_markup=markup)
    await Admin.check_order(msg, call.message)


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
            await bot.send_message(admin.id, f"Упал заказ номер {str(number)}")


@dp.message_handler(state=States.INSIDE, content_types=['text'])
async def inside_handler(message: types.Message):
    msg = message.text.lower()
    id = str(message.chat.id)
    if "назад" in msg:
        await States.ADMIN.set()
        markup = get_markup('admin_main', id=id)
        await message.answer('Главное меню админки', reply_markup=markup)
    else:
        article, cnt, pvz_cnt = msg.split(' ')
        


@dp.message_handler(state=States.ADMIN_ADDRESS_DISTRIBUTION)
async def address_distribution_handler(message: types.Message):
    msg = message.text
    id = str(message.chat.id)
    _msg = msg.lower()
    if ('проверить ботов' in _msg) or ("cделать выкуп" in _msg) or ("добавить пользователя" in _msg) or ("назад" in _msg):
        await States.ADMIN.set()
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
    msg = message.text.lower()

    user = Users.load(id)

    name = msg
    user.set(name=name)
    user.update()

    await States.FF_ADDRESS_END.set()
    await message.answer('Напишите адрес вашего ФФ')

@dp.message_handler(state=States.FF_ADDRESS_END)
async def ff_address_end_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text.lower()

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

    if ('проверить ботов' in msg) or ("cделать выкуп" in msg) or ("добавить пользователя" in msg) or ("назад" in msg):
        await States.ADMIN.set()
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
    msg = message.text.lower()

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
            Addresses.insert(Address(address=address, tg_id=id))

        addresses_to_print = "".join(map(lambda x: x + '\n', [address for address in user.addresses]))

        markup = get_markup('pup_addresses')
        await message.answer(
            f'Это все адреса?\n\n{addresses_to_print}\nЕсли есть еще адреса напишите их?\n\nЕсли это все адреса, просто напишите "Всё"',
            reply_markup=markup)

    user.update()


if __name__ == '__main__':
    executor.start_polling(dp)
