from aiogram import types


def get_markup(markup_name, role='', is_admin=False, id=''):
    if 'pup_addresses' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Всё")

        return markup
    elif 'admin_main' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("🔍 Поиск товаров 🔎")
        markup.add("💰 Выкуп собраных заказов 💰")
        markup.add("➕ Добавить пользователя ➕")
        # markup.add("💼 Авторизоваться в партнёрку 💼")
        if id:
            if id == '794329884' or id == '535533975':
                markup.add("🤖 Открыть бота 🤖")
                markup.add("🕙 Проверить ожидаемое 🕑")
        markup.add("✉ Проверить адреса ✉")
        markup.add("🏡 Распределить адреса по ботам 🏡")
        markup.add("◄ Назад")

        return markup
    elif 'main_order' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Файл")
        markup.add("Чат")
        markup.add("◄ Назад")

        return markup
    elif 'admin_add_user' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("По username")
        markup.add("Сгененрировать ключ")
        markup.add("◄ Назад")

        return markup
    elif 'main_main' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        if is_admin:
            markup.add("🌈 Admin")
        if role == "FF" or is_admin:
            markup.add("🚀 Собрать самовыкупы 🚀")
            markup.add("⛔ Собрать РЕАЛЬНЫЕ заказы 🚚")
            markup.add("📑 Список исключенных из сборки заказов 📑")
        if role == "PUP" or is_admin:
            markup.add("📊 Статистика 📊")
            markup.add("📓 Проверить ПВЗ 📓")
        else:
            markup.add("⚡ Регистрация ⚡")

        markup.add("◄ Назад")
        # markup.add("Настройки")

        return markup
    elif 'main_register' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Как ПВЗ")
        markup.add("Как сотрудник ФФ")
        markup.add("◄ Назад")
        # markup.add("Для выкупов")

        return markup
    elif 'only_back' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("◄ Назад")

        return markup
    elif '' == markup_name:
        pass

def get_list_keyboard(keys):
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    for key in keys:
        btns += [types.InlineKeyboardButton(text=key, callback_data=key)]

    keyboard.add(*btns)
    return keyboard

def get_keyboard(keyboard_name, *args):
    if 'admin_bots' == keyboard_name:
        keyboard = types.InlineKeyboardMarkup()
        bots = []
        bots_name = args[0]
        for bot_name in bots_name:
            bots += [types.InlineKeyboardButton(text=bot_name, callback_data=bot_name)]
        keyboard.add(*bots)

        return keyboard
    elif 'admin_bot_search' == keyboard_name:
        keyboard = types.InlineKeyboardMarkup()
        btns = []
        btns += [types.InlineKeyboardButton(text='90852969', callback_data='90852969')]
        btns += [types.InlineKeyboardButton(text='Школьный портфель 94577084', callback_data='94577084')]
        # btns += [types.InlineKeyboardButton(text='90086484', callback_data='90086484')]
        # btns += [types.InlineKeyboardButton(text='90633439', callback_data='90633439')]
        keyboard.add(*btns)

        return keyboard
