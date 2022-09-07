# Python Modules
from datetime import datetime, timedelta
from asyncio import sleep
import io
import random

import asyncio
import ujson
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

# For telegram api
from aiogram import Bot as TG_Bot
from aiogram import Dispatcher, executor, types
from aiogram.utils.json import json
from loguru import logger

from TG.Bot import bot_buy
from TG.BotEvents import BotEvents
from TG.Admin import Admin
from TG.Models.BotEvents import BotsEvents_Model, BotEvent_Model
from TG.Models.Addresses import Addresses_Model, Address_Model
from TG.Models.ExceptedDeliveries import ExceptedDeliveries_Model, ExceptedDelivery_Model
from TG.Models.Delivery import Deliveries_Model
from TG.Models.OrdersOfOrders import OrderOfOrders_Model, OrdersOfOrders_Model
from TG.Models.Users import Users_Model, User_Model
from TG.Models.Bots import Bots_Model
from TG.Models.Whitelist import Whitelist_Model
from TG.Models.Admins import Admin_Model as Admin_model
from TG.Markups import get_markup, get_keyboard, get_list_keyboard
from TG.States import States
from WB.Partner import Partner

from configs import config

import pandas as pd

DEBUG = config['DEBUG']

API_TOKEN = config['tokens']['telegram']
# Initialize bot and dispatcher
tg_bot = TG_Bot(token=API_TOKEN)
loop = asyncio.get_event_loop()
dp = Dispatcher(tg_bot, storage=MemoryStorage(), loop=loop)


@dp.message_handler(text='◄ Назад', state="*")
async def back_handler(message: types.Message, state: FSMContext):
    id = str(message.chat.id)
    is_admin = Admin.is_admin(id)
    if is_admin:
        current_state = await state.get_state()
        if current_state == "States:ADMIN" or current_state is None:
            markup = get_markup('main_main', is_admin=is_admin)
        else:
            await States.ADMIN.set()
            markup = get_markup('admin_main', id=id)
            await message.answer('Вы в меню Админа', reply_markup=markup)
            return
    else:
        markup = get_markup('main_main', Users_Model.load(id).role)
    await state.set_data({})
    await States.MAIN.set()
    await message.answer('Главное меню', reply_markup=markup)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    username = message.chat.username
    id = str(message.chat.id)
    print(username, id, 'is started')
    whitelisted = Whitelist_Model.check(id)
    if whitelisted:
        await States.MAIN.set()
        is_admin = Admin.is_admin(id)
        if is_admin:
            markup = get_markup('main_main', is_admin=is_admin)
        else:
            user = Users_Model.load(id)
            if user:
                markup = get_markup('main_main', user.role)
            else:
                markup = get_markup('main_main')
        await message.reply("Привет", reply_markup=markup)
    elif username:
        wl = Whitelist_Model.set_tg_id(id, username=username)
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
    wl = Whitelist_Model.set_tg_id(id, secret_key=secret_key)
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
    id = str(message.chat.id)
    user = Users_Model.load(id)

    logger.info(user)

    if not user:
        if "⚡ регистрация ⚡" in msg:
            await States.REGISTER.set()
            markup = get_markup('main_register')
            await message.answer("Как вы хотите зарегистрировать:", reply_markup=markup)
            return
    elif user.role in "FF":
        if "🚀 собрать самовыкупы 🚀" in msg:
            # deliveries = Deliveries_Model.load(collected=False, inn="771375894400")
            # for delivery in deliveries:
            #     await message.answer(f'Артикулы заказа {delivery.articles}\n\n'
            #                          f'Адрес заказа {delivery.pup_address}\n\n'
            #                          f'Время заказа {delivery.start_date}')
            # await message.answer('⛔ 🚀 Сборка самовыкупов пока не доступна 🚀 ⛔')
            users = Users_Model.load(role='IE')
            ies = [user.ie for user in users]
            logger.info(ies)
            await States.COLLECT_ORDERS.set()
            markup = get_list_keyboard(ies)
            logger.info(markup)
            await message.answer('Выберите ИП, по которому хотите собрать самовыкупы', reply_markup=markup)
            return
        elif "⛔ собрать реальные заказы 🚚" in msg:
            await message.answer('⛔ Сборка РЕАЛЬНЫХ заказов ПОКА НЕДОСТУПНА ⛔')
            # users = Users.load(role='IE')
            # ies = [user.ie for user in users]
            # print(ies)
            # await States.COLLECT_OTHER_ORDERS.set()
            # markup = get_list_keyboard(ies)
            # await message.answer('Выберите ИП, по которому хотите собрать заказы', reply_markup=markup)
            return
        elif "📑 список исключенных из сборки заказов 📑" in msg:
            users = Users_Model.load(role='IE')
            if users:
                ies = [user.ie for user in users]
                print(ies)
                await States.EXCEPTED_ORDERS_LIST.set()
                markup = get_list_keyboard(ies)
                await message.answer('Выберите ИП, по которому хотите посмотреть или изменить список',
                                     reply_markup=markup)
                return
            else:
                await message.answer('Ни одно ИП не найдено')
                return
    elif user.role in "PUP":
        if "📊 статистика 📊" in msg:
            # deliveries = Deliveries_Model.load_stat(pup_tg_id="791436094")
            deliveries = Deliveries_Model.load_stat(pup_tg_id=id)
            if deliveries:
                msg = "📊 <b>Статистика за месяц:</b> 📅\n\n"

                total_price_str = str(sum([delivery.total_price for delivery in deliveries]))
                total_price = ''.join(
                    [p + ' ' if (len(total_price_str) - i) % 3 == 1 else p for i, p in enumerate(total_price_str)])
                msg += f"<b>Оборот:</b> {total_price}₽\n" \
                       f"<b>Заказы:</b> {sum([sum(delivery.quantities) for delivery in deliveries])} 📦\n"

                addresses_list = list(set(delivery.pup_address for delivery in deliveries))
                cities_list = list(set(delivery.pup_address.split(",")[0] for delivery in deliveries))

                stat = []
                for i, address in enumerate(addresses_list):
                    stat += [{}]
                    stat[i]['cnt'] = 0
                    stat[i]['total_price'] = 0
                    stat[i]['fbo_cnt'] = 0

                    for delivery in deliveries:
                        if delivery.pup_address == address:
                            stat[i]['address'] = address
                            stat[i]['total_price'] += delivery.total_price
                            stat[i]['cnt'] += 1
                            print(delivery.statuses)
                            if "FBO" in delivery.statuses:
                                stat[i]['fbo_cnt'] += sum(1 if status == "FBO" else 0 for status in delivery.statuses)

                stat = sorted(stat, key=lambda o: o['total_price'], reverse=True)

                # msg += "\n📫 <b>На каждый адрес</b> 📫\n"
                for city in cities_list:
                    msg += f"\n🏬 <u><b>{city.title()}:</b></u>\n"
                    for s in stat:
                        if city in s['address']:
                            total_price_str = str(s['total_price'])
                            total_price = ''.join([p + ' ' if (len(total_price_str) - i) % 3 == 1 else p for i, p in
                                                   enumerate(total_price_str)])

                            msg += f"\n📫 <b>{','.join(s['address'].split(',')[1:]).title()}:</b>\n" \
                                   f"<b>Оборот:</b> {total_price}₽\n" \
                                   f"<b>Заказы:</b> {s['cnt']} 📦\n"
            else:
                msg = "<b>На ваши ПВЗ еще не было заказов в этом месяце</b>"

            await message.answer(msg, parse_mode="HTML")
            return
        elif "📓 проверить пвз 📓" in msg:
            # deliveries = Deliveries_Model.load_check_state(pup_tg_id="791436094")
            deliveries = Deliveries_Model.load_check_state(pup_tg_id=id)
            if deliveries:
                msg = "📓 <b>Состояния ПВЗ</b> 📓\n\n"

                addresses_list = list(set(delivery.pup_address for delivery in deliveries))
                cities_list = list(set(delivery.pup_address.split(",")[0] for delivery in deliveries))

                is_fbos_cnt = 0

                stat = []
                for i, address in enumerate(addresses_list):
                    stat += [{}]
                    stat[i]['cnt'] = 0
                    stat[i]['fbo_cnt'] = 0
                    stat[i]['articles'] = []
                    for delivery in deliveries:
                        if delivery.pup_address == address:
                            stat[i]['address'] = address
                            stat[i]['cnt'] += 1
                            print("FBO" in delivery.statuses, delivery.statuses)
                            if "FBO" in delivery.statuses:
                                is_fbos_cnt += 1
                                is_fbos = [1 if status == "FBO" else 0 for status in delivery.statuses]
                                stat[i]['fbo_cnt'] += sum(is_fbos)
                                for j, is_fbo in enumerate(is_fbos):
                                    if is_fbo:
                                        in_articles = [delivery.articles[j] in article for article in stat[i]['articles']]
                                        if any(in_articles):
                                            index = in_articles.index(True)
                                            splited = stat[i]['articles'][index].split(' ')
                                            stat[i]['articles'][index] = splited[0] + " " + str(int(splited[1]) + 1)
                                        else:
                                            stat[i]['articles'] += [delivery.articles[j] + " 1"]
                if is_fbos_cnt:
                    stat = sorted(stat, key=lambda o: o['fbo_cnt'], reverse=True)

                    # msg += "\n📫 <b>Товары физически на ПВЗ</b> 📫\n"
                    for city in cities_list:
                        _msg = f"\n🏬 <u><b>{city.title()}:</b></u>\n"

                        is_have_fbo_cnt = False
                        for s in stat:
                            if city in s['address']:
                                if s['fbo_cnt']:
                                    is_have_fbo_cnt = True
                                    _msg += f"\n📫 <b>{','.join(s['address'].split(',')[1:]).title()}:</b>\n" \
                                            f"<b>Товары физически на ПВЗ:</b> {s['fbo_cnt']} 📦\n"
                                    _msg += f"<b>Артикул     кол-во</b>\n"
                                    for article in s['articles']:
                                        _msg += f"{'   '.join(article.split(' '))} шт.\n"
                        if is_have_fbo_cnt:
                            msg += _msg
                else:
                    msg = "<b>Для ваших ПВЗ еще не рассчитаны показатели</b>"
            else:
                msg = "<b>Для ваших ПВЗ еще не рассчитаны показатели</b>"

            await message.answer(msg, parse_mode="HTML")
            return
    is_admin = Admin.is_admin(id)
    if is_admin:
        if "🌈 admin" in msg:
            await set_admin(message)
            return


@dp.message_handler(state=States.REGISTER)
async def register_handler(message: types.Message):
    msg = message.text.lower()
    id = str(message.chat.id)

    if "как пвз" in msg:
        id = str(message.chat.id)
        user = Users_Model.load(id)
        if not user:
            user = User_Model(id, role='PUP')
            user.insert()

        await States.PUP_ADDRESSES_START.set()
    elif "как сотрудник фф" in msg:
        id = str(message.chat.id)
        user = Users_Model.load(id)
        if not user:
            user = User_Model(id, role='FF')
            user.insert()

        await States.FF_ADDRESS_START.set()
    elif "назад" in msg:
        await States.MAIN.set()
        markup = get_markup('main_main')
        await message.reply("Привет", reply_markup=markup)

    await message.answer("Ваше ФИО?")


@dp.message_handler(state=States.ADMIN)
async def admin_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text.lower()
    print(msg)

    if "💰 создать заказ 💰" in msg:
        await States.CREATE_ORDER.set()
        await message.answer("Введите: Название для заказа")
    elif "👀 посмотреть заказы 👀" in msg:
        await States.WATCH_ORDER.set()
        keyboard = get_keyboard('admin_watch_orders_group')
        await message.answer("Введите: Название для заказа", reply_markup=keyboard)
    elif "✏️ редактировать заказы ✏️" in msg:
        await States.EDIT_ORDER.set()
        await message.answer("Введите: Название для заказа")
    elif "🔍 поиск товаров 🔎" in msg:
        keyboard = get_keyboard('admin_bot_search')
        await message.answer('Пришлите Excel файл заказа\n'
                             'Или выберите артикул и выкупиться 1 товар с таким артикулом', reply_markup=keyboard)
        await States.BOT_SEARCH.set()
    elif "💰 выкуп собраных заказов 💰" in msg:
        bots_event = BotsEvents_Model.load(event="FOUND")
        if bots_event:
            await message.answer(f'{len(bots_event)} ботов ожидают выкупа, скольких вы хотите выкупить?')
            await message.answer('<b>ФИЧА</b>: <i>нажмите кнопку</i> <b>"💰 выкуп собраных заказов 💰"</b> <i>для того, чтобы выкупить</i> <b>только один</b>.', parse_mode="HTML")
            await States.BOT_BUY.set()
        else:
            markup = get_markup('admin_main', id=id)
            await message.answer('----------🎉Поздравляю!🎉--------\n'
                                 '💲Вы выкупили все заказы!💲', reply_markup=markup)
    elif "💸 повторный выкуп 💸" in msg:
        await States.RE_BUY.set()
        tg_bots = Bots_Model.load_with_balance()
        bots_name = [f"{tg_bots[i].name} {tg_bots[i].balance} ₽" for i in range(len(tg_bots))]
        markup = get_keyboard('admin_bots', bots_name)
        await message.answer('Выберите бота', reply_markup=markup)
    elif "➕ добавить пользователя ➕" in msg:
        await States.TO_WL.set()
        markup = get_markup('admin_add_user')
        await message.answer('Выберите способ', reply_markup=markup)
    elif "💼 авторизоваться в партнёрку 💼" in msg:
        await States.AUTH_PARTNER.set()
        markup = get_markup('only_back')
        await message.answer('Введите номер телефона в формате 9XXXXXXX\n'
                             'Сообщение на повторную отправку придёт автоматически', reply_markup=markup)
    elif "🕙 проверить ожидаемое 🕑" in msg:
        deliveries = Deliveries_Model.load(active=True, pred_end_date=datetime.now())
        if deliveries:
            await States.CHECK_WAITS.set()
            bots_name = []
            for delivery in deliveries:
                # print(delivery)
                # is_delivery_wait_exist = BotsWait_Model.check_exist_delivery_wait(delivery.bot_name, delivery.id)
                # if not is_delivery_wait_exist:
                #     bot_event = BotWait_Model(bot_name=delivery.bot_name, event='delivery', start_datetime=datetime.now(),
                #                              end_datetime=delivery.pred_end_date, wait=False,
                #                              data=json.dumps('{"id": ' + str(delivery.id) + '}'))
                #     bot_event.insert()
                if delivery.bot_name not in bots_name:
                    bots_name += [delivery.bot_name]
            keyboard = get_keyboard('admin_bots', bots_name)
            await message.answer('Выберите бота', reply_markup=keyboard)
        else:
            await States.ADMIN.set()
            await message.answer('Все товары доставлены')
        return
    elif "💵 проверить баланс всех ботов 💵" in msg:
        await States.CHECK_BOTS_BALANCE.set()
        keyboard = get_keyboard('yes_or_no')
        await message.answer('Вы уверены, что хотите запустить проверку балансов всех ботов?', reply_markup=keyboard)
        return
    elif '✉ проверить адреса ✉' in msg:
        res_message, state = Admin.check_not_checked_pup_addresses()
        markup = get_markup('admin_main', id=id)
        await message.answer(res_message, reply_markup=markup)
        await getattr(States, state).set()
    elif '🏡 распределить адреса по ботам 🏡' in msg:
        res_message, state = Admin.check_not_added_pup_addresses()
        markup = get_markup('admin_main', id=id)
        await message.answer(res_message, reply_markup=markup)
        await getattr(States, state).set()
    else:
        if "🤖 открыть бота 🤖" in msg or "🤖 статус ботов 🤖" in msg:
            if id == '794329884' or id == '535533975':
                if "🤖 открыть бота 🤖" in msg:
                    await States.RUN_BOT.set()
                    bots = Bots_Model.load()
                    bots_name = [f"{bots[i].name}" for i in range(len(bots))]
                    bots_name.sort()
                    # markup = get_keyboard('admin_bots', bots_name)
                    await message.answer('Введите имя бота')
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
    inn = ''
    if article in ['90852969']:
        # category = 'Женщинам;Пляжная мода;Купальники'
        search_key = 'Купальник слитный женский белый'
        inn = '381108544328'
    if article in ['90086484']:
        # category = 'Женщинам;Пляжная мода;Купальники'
        search_key = 'Купальник раздельный'
        inn = '381108544328'
    if article in ['90633439']:
        # category = 'Женщинам;Пляжная мода;Купальники'
        search_key = 'Женский раздельный купальник без пуш ап'
        inn = '381108544328'
    if article in ['94577084']:
        # category = 'Женщинам;Пляжная мода;Купальники'
        search_key = 'Школьный портфель'
        # inn = '381108544328'

    await States.ADMIN.set()

    goods = [[article, search_key, category, "1", "1", inn]]
    await call.message.edit_text(f'Начался поиск артикула {article}')

    data_for_bots, status_fail = await Admin.get_data_of_goods(goods)
    if status_fail:
        await call.message.answer(f'❌ Поиск артикула {article} упал на анализе карточки ❌')

    res_msg = ''
    msgs = ''
    if DEBUG:
        msgs = await Admin.bot_search(data_for_bots)
    else:
        try:
            msgs = await Admin.bot_search(data_for_bots)
        except:
            await call.message.answer(f'❌ Поиск артикула {article} упал ❌')
    try:
        for msg in msgs:
            res_msg += msg + "\n"
    except:
        pass

    res_msg += '\n' + f'Поиск артикула {article} завершен'

    await call.message.answer(res_msg)


@dp.message_handler(state=States.AUTH_PARTNER, content_types=['text'])
async def inside_handler(message: types.Message, state: FSMContext):
    msg = message.text
    id = str(message.chat.id)
    state_data = await state.get_data()

    if state_data.get('number') == None:
        number = str(int(msg))
        state_data['number'] = number
        await state.set_data(state_data)
    else:
        number = state_data['number']

    try:
        # проверяем код
        code = str(int(msg))
    except:
        await message.answer('Суда нужно вводить код\n'
                             'Код должен быть цифрами')
        return
    if state_data.get("driver") == None:
        partner_bot = Partner()
        await partner_bot.auth(number)
        await message.answer('Ожидайте код')
        state_data['driver'] = partner_bot.driver
        await state.set_data(state_data)


@dp.callback_query_handler(state=States.RUN_BOT)
async def run_bot_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data
    # bot_name, bot_type = msg.split(' ')
    bot_name = msg
    await States.ADMIN.set()
    await call.message.edit_text(msg + " открыт")
    await Admin.open_bot(bot_name=bot_name)


@dp.message_handler(state=States.RUN_BOT)
async def run_bot_message_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text
    bot_name = msg
    await States.ADMIN.set()
    await message.answer(msg + " открыт")
    await Admin.open_bot(bot_name=bot_name)


@dp.callback_query_handler(state=States.CHECK_WAITS)
async def check_waits_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data
    await States.ADMIN.set()
    await call.message.edit_text(msg + " открыт")
    await Admin.check_delivery(msg, call.message)

@dp.callback_query_handler(state=States.CHECK_BOTS_BALANCE)
async def check_waits_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data

    await States.ADMIN.set()
    if msg == "yes":
        all_bots = Bots_Model.load(_type="WB")
        print([bot.name for bot in all_bots])
        print(len([bot.name for bot in all_bots]))
        random.shuffle(all_bots)
        start_date = datetime.now()
        minutes = 0
        for bot in all_bots:
            minutes += random.randint(1,4)
            BotEvent_Model(bot_name=bot.name, event="CHECK_BALANCE", wait=True, datetime_to_run=start_date + timedelta(minutes=minutes, seconds=random.randint(0, 59))).insert()

        await call.message.edit_text(msg)

@dp.callback_query_handler(state=States.COLLECT_OTHER_ORDERS)
async def collect_other_deliveries_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    ie = call.data
    inn = Users_Model.load(ie=ie).inn
    await States.MAIN.set()

    await call.message.edit_text(f'Началась сборка РЕАЛЬНЫХ заказов по {ie}')

    await Partner().collect_other_deliveries(inn)

    await call.message.answer(f'Закончилась сборка РЕАЛЬНЫХ заказов по {ie}')


@dp.callback_query_handler(state=States.COLLECT_ORDERS)
async def collect_deliveries_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    ie = call.data
    inn = Users_Model.load(ie=ie).inn
    await States.MAIN.set()

    await call.message.edit_text(f'Началась сборка самовыкупов по {ie}')
    if id != "794329884":
        await tg_bot.send_message("794329884", f'Началась сборка самовыкупов по {ie}')

    res = await Partner().collect_deliveries(inn)
    res_msg = ''
    for r in res:
        res_msg += r + "\n\n"
    if ('Не найден заказ' not in res_msg) and ('Самовыкупов по данному ИП нет' not in res_msg) \
            and ('Слетела авторизация в аккаунт Партнёров' not in res_msg):
        res_msg = '✅ Все заказы собраны успешно ✅' + '\n\n'

    await call.message.answer(res_msg + f'Закончилась сборка самовыкупов по {ie}')
    if id != "794329884":
        await tg_bot.send_message("794329884", res_msg + f'Закончилась сборка самовыкупов по {ie}')


@dp.callback_query_handler(state=States.EXCEPTED_ORDERS_LIST)
async def excepted_deliveries_callback_query_handler(call: types.CallbackQuery, state: FSMContext):
    id = str(call.message.chat.id)
    ie = call.data
    inn = Users_Model.load(ie=ie).inn
    excepted_deliveries = ExceptedDeliveries_Model.load(inn=inn)
    await state.update_data(inn=inn)

    if excepted_deliveries:

        res_msg = f"Для клиента {ie} исключены заказы с номерами:"
        for ed in excepted_deliveries:
            res_msg += "\n" + ed.delivery_number
        res_msg += f"\n\nНапишите номера заказов,которые хотите изменить или добавить"
    else:
        res_msg = f"У клиента {ie} нет исключенных заказов"
        res_msg += f"\n\nНапишите номера заказов, которые хотите исключить"
    await States.EXCEPTED_ORDERS_LIST_CHANGE.set()
    await call.message.edit_text(res_msg)


@dp.message_handler(state=States.EXCEPTED_ORDERS_LIST_CHANGE)
async def excepted_deliveries_change_handler(message: types.Message, state: FSMContext):
    msg = message.text
    id = str(message.chat.id)
    delivery_numbers = msg.replace("\n", " ").strip().split(" ")

    data = await state.get_data()
    inn = data['inn']
    excepted_deliveries = ExceptedDeliveries_Model.load(inn=inn)

    if excepted_deliveries:
        local_delivery_numbers = [ed.delivery_number for ed in excepted_deliveries]

    added = []
    deleted = []
    for delivery_number in delivery_numbers:
        try:
            i = local_delivery_numbers.index(delivery_number)
            print(i)
            excepted_deliveries[i].delete()
            deleted += [delivery_number]
        except:
            eo = ExceptedDelivery_Model(inn=inn, delivery_number=delivery_number, start_datetime=datetime.now())
            eo.insert()
            added += [delivery_number]

    res_msg = ""
    if len(added):
        res_msg = f"Добавлены заказы:"
        for delivery_number in added:
            res_msg += "\n" + delivery_number

        if len(deleted):
            res_msg += "\n"
    if len(deleted):
        res_msg += "\n" + "Удалены заказы:"
        for delivery_number in deleted:
            res_msg += "\n" + delivery_number

    ie = Users_Model.load(inn=inn).ie
    excepted_deliveries = ExceptedDeliveries_Model.load(inn=inn)

    if excepted_deliveries:
        res_msg += "\n\n" + f"Для клиента {ie} исключены заказы с номерами:"
        for eo in excepted_deliveries:
            res_msg += "\n" + eo.delivery_number
    else:
        res_msg += "\n\n" + f"Для клиента {ie} нет исключеных заказов"

    await States.MAIN.set()
    markup = get_markup('main_main', Users_Model.load(id).role)
    await message.answer(res_msg, reply_markup=markup)


@dp.message_handler(state=States.TO_WL)
async def to_whitelist_handler(message: types.Message):
    msg = message.text
    id = str(message.chat.id)
    if msg.lower() in 'по username':
        await message.answer("Введите username пользователя")
    elif msg.lower() in 'сгененрировать ключ':
        secret_key = Admin.generate_secret_key()

        Whitelist_Model(secret_key=secret_key).insert()

        await States.ADMIN.set()
        markup = get_markup('admin_main', id=id)
        await message.answer("Ключ для идентификации:")
        await message.answer(secret_key, reply_markup=markup)
    elif "@" in msg:
        username = msg[1:]
        Whitelist_Model(username=username).insert()

        await States.ADMIN.set()
        markup = get_markup('admin_main', id=id)
        await message.answer(f"Пользователь с username {msg} добавлен", reply_markup=markup)


@dp.message_handler(state=States.BOT_BUY, content_types=['text'])
async def bot_buy_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text
    if msg.lower() == "💰 выкуп собраных заказов 💰":
        bots_cnt = 1
    else:
        try:
            bots_cnt = int(msg)
        except:
            await message.answer('Вы указали не цифру, укажите цифру')
            return

    await States.ADMIN.set()

    await message.answer('Выкуп начался')

    await Admin.bot_buy(message, bots_cnt)


@dp.message_handler(state=States.RE_BUY)
async def re_bot_buy_handler(message: types.Message, state: FSMContext):
    id = str(message.chat.id)
    msg = message.text

    # Первым был введён артикул, всё последующее - это ключевое слово
    article = msg.split(' ')[0]
    search_key = msg[len(article) + 1:]

    # Получаем имя бота, которые было указано в предыдущем шаге обработки операции
    data = await state.get_data()
    bot_name = data['bot_name']

    logger.info(f"{bot_name} {article} {search_key}")

    # Возвращаем состояние на обработку команд для Адимина,
    # чтобы всё введенное после, снова обрабатывалось обработчиком админа
    await States.ADMIN.set()

    # Получаем текуще активное событие
    bot_event = BotsEvents_Model.load(bot_name=bot_name, wait=True)
    logger.info(bot_event)

    # Определяем необходимость поиска или только выкуп
    is_go_search = True
    is_go_buy = True
    if bot_event:
        bot_event = bot_event[0]
        if bot_event.event == "RE_FOUND":
            is_go_search = False
            is_go_buy = True
        try:
            int(article)
        except:
            is_go_search = False
            is_go_buy = False

    logger.info(f"is_go_search = {is_go_search}\nis_go_buy = {is_go_buy}")

    # Поиск
    if is_go_search:
        # формируем данные о заказе
        goods = [[article, search_key, '', "1", "1", "381108544328"]]
        await message.answer(f'Начался поиск артикула {article}')

        # собираем все данные о конкретных товарах
        data_for_bots, status_fail = await Admin.get_data_of_goods(goods)
        if status_fail:
            await message.answer(f'❌ Поиск артикула {article} упал на анализе карточки ❌')
        else:
            msgs = ''
            res_msg = ''
            # Запускаем поиск заказа
            if DEBUG:
                msgs = await Admin.bot_re_search(bot_name, data_for_bots)
            else:
                try:
                    msgs = await Admin.bot_re_search(bot_name, data_for_bots)
                except:
                    await message.answer(f'❌ Поиск артикула {article} упал ❌')
            try:
                for msg in msgs:
                    res_msg += msg + "\n"
            except:
                pass

            res_msg += '\n' + f'Поиск артикула {article} завершен'

            await message.answer(res_msg)

    # Выкуп
    if is_go_buy:
        await message.answer('Выкуп начался')

        # Если до этого не существовало активного события, получаем текуще активное событие по боту
        if not bot_event:
            bot_event = BotsEvents_Model.load(bot_name=bot_name, wait=True)

        if bot_event:
            bot_event = bot_event[0]

            # запускаем выкуп
            await Admin.bot_re_buy(message, bot_event)

            res_msg = f"Завершен выкуп по боту: {bot_name}"

            await message.answer(res_msg)
        await message.answer("ERROR")


@dp.callback_query_handler(state=States.RE_BUY)
async def excepted_deliveries_callback_query_handler(call: types.CallbackQuery, state: FSMContext):
    id = str(call.message.chat.id)
    msg = call.data
    logger.info(msg)

    bot_name, balance, _ = msg.split(" ")
    await state.set_data({'bot_name': bot_name})

    await call.message.answer('Укажите артикул и ключевую фразу для бота')


@dp.message_handler(state=States.ADMIN_ADDRESS_DISTRIBUTION)
async def address_distribution_handler(message: types.Message):
    msg = message.text
    id = str(message.chat.id)

    bots_data_str = msg.split('\n\n')

    for bot_data in bots_data_str:
        bot_data = bot_data.split('\n')

        name = bot_data[0]
        new_addresses = bot_data[1:]

        wb_bot = Bots_Model.load(name=name)
        wb_bot.append(addresses=new_addresses)
        wb_bot.update()

        for address in new_addresses:
            address = Addresses_Model.load(address=address)
            address.set(added_to_bot=True)
            address.update()

    await States.ADMIN.set()
    markup = get_markup('admin_main', id=id)
    await message.answer('Все адреса добавлены в ботов', reply_markup=markup)


@dp.message_handler(state=States.FF_ADDRESS_START)
async def ff_address_start_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text

    user = Users_Model.load(id)

    name = msg
    user.set(name=name)
    user.update()

    await States.FF_ADDRESS_END.set()
    await message.answer('Напишите адрес вашего ФФ')


@dp.message_handler(state=States.FF_ADDRESS_END)
async def ff_address_end_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text

    user = Users_Model.load(id)

    address = msg
    user.append(addresses=[address])
    user.update()

    await States.MAIN.set()

    is_admin = Admin.is_admin(id)
    if is_admin:
        markup = get_markup('main_main', is_admin=is_admin)
    else:
        markup = get_markup('main_main', Users_Model.load(id).role)
    await message.answer('Мы запомнили ваши данные', reply_markup=markup)


@dp.message_handler(state=States.ADMIN_ADDRESS_VERIFICATION)
async def address_verification_handler(message: types.Message):
    msg = message.text
    id = str(message.chat.id)

    new_addresses = msg.split('\n')

    all_not_checked_addresses = Addresses_Model.get_all_not_checked()

    for i, old_address_str in enumerate(all_not_checked_addresses):
        address = Address_Model().load(address=old_address_str)
        address.append(address=new_addresses[i])
        address.update()

        user = Users_Model.load(id=address.tg_id)
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

    user = Users_Model.load(id)

    name = msg
    user.set(name=name)
    user.update()

    await States.PUP_ADDRESSES_CONTINUE.set()
    await message.answer('Напишите адреса ваших ПВЗ\n\n'
                         'Каждый адрес с новой строчки или каждый адрес в отдельном сообщении\n\n'
                         'Пример:\n'
                         'г Москва, Чистопрудная улица 32к2\n'
                         'г Москва, Вавиловская улица 22к8')


@dp.message_handler(state=States.CREATE_ORDER)
async def create_order_handler(message: types.Message, state: FSMContext):
    id = str(message.chat.id)
    msg = message.text

    data = await state.get_data()

    if 'order_name' not in data.keys():
        order_name = msg

        await state.set_data({"order_name": order_name})

        await message.answer('Введите ИИН клиента')
        return
    elif 'inn' not in data.keys():
        try:
            inn = str(int(msg))

            data['inn'] = inn

            await state.set_data(data)

            await message.answer('Введите артикулы')
        except:
            await message.answer('ИНН должно состоять только из цифр')
        return
    elif 'articles' not in data.keys():
        articles = msg.replace("\n", " ").strip().split(" ")

        try:
            # проверяем артикулы
            [int(article) for article in articles]

            data["articles"] = articles
            await state.set_data(data)

            await message.answer('Сколько нужно сделать выкупов каждого артикула')
        except:
            await message.answer('Артикулы должно состоять только из цифр')
        return
    elif 'quantities_to_bought' not in data.keys():
        quantities_to_bought = msg.replace("\n", " ").strip().split(" ")

        logger.info(quantities_to_bought)

        try:
            if len(quantities_to_bought) == 1:
                quantities_to_bought = [int(quantities_to_bought[0]) for _ in range(len(data['articles']))]
            else:
                quantities_to_bought = [int(quantity_to_bought) for quantity_to_bought in quantities_to_bought]

            data["quantities_to_bought"] = quantities_to_bought
            await state.set_data(data)

            await message.answer(f'Ключевые слова для артикула\n\n'
                                 f'{data["articles"][0]}', parse_mode="HTML")
        except:
            await message.answer('Кол-во выкупов каждого артикула должно быть цифрами')
        return
    elif 'search_keys' not in data.keys():
        search_keys = msg

        data['search_keys'] = [search_keys]
        await state.set_data(data)
        if len(data['articles']) > 1:
            await message.answer(f'Ключевые слова для артикула\n\n'
                                 f'{data["articles"][1]}', parse_mode="HTML")
        else:
            await message.answer('Сколько комментариев нужно оставить на каждый артикул')
        return
    elif len(data['search_keys']) < len(data['articles']):
        search_keys = msg

        data['search_keys'] += [search_keys]
        await state.set_data(data)
        logger.info(f"{len(data['search_keys'])} {len(data['articles'])}")
        if len(data['search_keys']) == len(data['articles']):
            await message.answer('Сколько комментариев нужно оставить на каждый артикул')
        else:
            await message.answer(f'Ключевые слова для артикула\n\n'
                                 f'{data["articles"][len(data["search_keys"])]}', parse_mode="HTML")
        return
    elif 'numbers_of_comments' not in data.keys():
        numbers_of_comments = msg.replace("\n", " ").strip().split(" ")

        try:
            if len(numbers_of_comments) == 1:
                numbers_of_comments = [int(numbers_of_comments[0]) for _ in range(len(data['articles']))]
            else:
                numbers_of_comments = [int(number_of_comments) for number_of_comments in numbers_of_comments]

            data['numbers_of_comments'] = numbers_of_comments
            await state.set_data(data)

            await message.answer(f'<i>Каждый с новой строчки</i>\n\n'
                                 f'Комментарии для артикула\n\n'
                                 f'{data["articles"][0]} <b>{data["search_keys"][0]}</b>', parse_mode="HTML")
        except:
            await message.answer('Кол-во комментариев должно быть цифрами')
        return
    elif 'comments' not in data.keys():
        comments = msg.strip().split("\n")

        data['comments'] = [comments]
        await state.set_data(data)

        if len(data['articles']) > 1:
            await message.answer(f'<i>Каждый с новой строчки</i>\n\n'
                                 f'Комментарии для артикула\n\n'
                                 f'{data["articles"][1]} <b>{data["search_keys"][1]}</b>', parse_mode="HTML")
        else:
            await message.answer(f'Сколько делать выкупов в день?')
        return
    elif len(data['comments']) < len(data['articles']):
        comments = msg.strip().split("\n")

        data['comments'] += [comments]
        await state.set_data(data)

        if len(data['comments']) == len(data['articles']):
            await message.answer(f'Сколько делать выкупов в день?')
        else:
            await message.answer(f'<i>Каждый с новой строчки</i>\n\n'
                                 f'Комментарии для артикула\n\n'
                                 f'{data["articles"][len(data["comments"])]} <b>{data["search_keys"][len(data["comments"])]}</b>',
                                 parse_mode="HTML")
        return
    elif 'bought_per_day' not in data.keys():
        try:
            bought_per_day = int(msg)

            data['bought_per_day'] = bought_per_day
            await state.set_data(data)

            await message.answer(f'Какой бюджет?')
        except:
            await message.answer(f'Количество выкупов должно быть цифрой')
        return
    elif 'budget' not in data.keys():
        try:
            budget = int(msg)

            data['budget'] = budget
            await state.set_data(data)
        except:
            await message.answer(f'Бюджет должен быть цифрой')

    data['id'] = data['order_name']
    del data['order_name']
    data['remaining_budget'] = data['budget']
    data['start_datetime'] = datetime.now()
    try:
        await States.ADMIN.set()
        order = OrderOfOrders_Model(**data)
        order.insert()
        await message.answer('Заказ создан')
    except:
        await message.answer('Не удалось создать заказ')

    if order:
        BotEvents.BuildOrderFulfillmentProcess(order)

    await state.set_data({})


@dp.callback_query_handler(state=States.WATCH_ORDER)
async def watch_orders_callback_query_handler(call: types.CallbackQuery, state: FSMContext):
    id = str(call.message.chat.id)
    msg = call.data

    await States.ADMIN.set()
    if msg == 'Активные':
        orders = OrdersOfOrders_Model.load()
        for order in orders:
            res_msg = f"Заказ {order.id}\n" \
                      f"От: {order.start_datetime}\n\n" \
                      f"ИНН: {order.inn}\n" \
                      f"Бюджет: {order.budget}\n" \
                      f"Оставшийся бюджет: {order.remaining_budget}\n" \
                      f"Необходимо выкупать каждый день: {order.bought_per_day}\n\n"
            for i, article in enumerate(order.articles):
                res_msg += f"Артикул {article}\n" \
                           f"Кол-во необходимых выкупов: {order.quantities_to_bought[i]}\n" \
                           f"Кол-во уже выкуполеных: {order.quantities_bought[i]}\n" \
                           f"Ключевые слова: {order.search_keys[i]}\n" \
                           f"Оставлено комментариев: {len(order.left_comments[i]) if order.left_comments else 0}\n" \
                           f"Осталось комментариев: {len(order.unused_comments[i])}\n\n"

            await call.message.answer(res_msg)
    elif msg == 'По ИНН':
        orders = OrdersOfOrders_Model.load()


@dp.message_handler(state=States.PUP_ADDRESSES_CONTINUE)
async def pup_addresses_continue_handler(message: types.Message):
    id = str(message.chat.id)
    msg = message.text

    user = Users_Model.load(id)

    if msg.lower() == 'всё':
        await States.MAIN.set()

        is_admin = Admin.is_admin(id)
        if is_admin:
            markup = get_markup('main_main', is_admin=is_admin)
        else:
            markup = get_markup('main_main', Users_Model.load(id).role)
        await message.answer('Мы запомнили ваши данные', reply_markup=markup)
    else:
        new_addresses = [a for a in msg.splitlines() if a]

        user.append(addresses=new_addresses)

        for address in new_addresses:
            Address_Model(address=address, tg_id=id).insert()

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
    logger.info(f"{username} {id} in default")
    whitelisted = Whitelist_Model.check(id)
    if whitelisted:
        is_admin = Admin.is_admin(id)
        if is_admin:
            await States.ADMIN.set()
            await admin_handler(message)
        else:
            await States.MAIN.set()
            await main_handler(message)


@dp.callback_query_handler(text_contains='_bw_', state="*")
async def others_callback_query_handler(call: types.CallbackQuery):
    id = str(call.message.chat.id)
    msg = call.data
    bot_name = msg.split(" ")[1]

    bot_event = BotsEvents_Model.load(event="PAYMENT", bot_name=bot_name, wait=True)

    logger.info(msg)

    if bot_event:
        bot_event = bot_event[0]
        await call.message.edit_text('Начался выкуп')

        try:
            status = await bot_buy(call.message, bot_event)
        except:
            status = False

        if not status:
            keyboard = get_keyboard('admin_notify_for_buy', bot_event.bot_name)
            await call.message.edit_text("Можно запустить выкуп повторно", reply_markup=keyboard)
        elif type(status) is str:
            msg = status
            logger.info(msg)
            await call.message.answer(msg)

        await call.message.answer("Выкуп завершен")


if __name__ == '__main__':
    dp.loop.create_task(BotEvents(tg_bot).main())
    executor.start_polling(dp)
