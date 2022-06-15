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
        markup.add("⚡ Регистрация ⚡")
        # markup.add("Настройки")

        return markup
    elif 'main_register' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Как ПВЗ")
        markup.add("Как сотрудник ФФ")
        markup.add("◄ Назад")
        # markup.add("Для выкупов")

        return markup
    elif '' == markup_name:
        pass
    elif '' == markup_name:
        pass


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
        bots = []
        bots += [types.InlineKeyboardButton(text='90086267', callback_data='90086267')]
        bots += [types.InlineKeyboardButton(text='90086484', callback_data='90086484')]
        bots += [types.InlineKeyboardButton(text='90086527', callback_data='90086527')]
        bots += [types.InlineKeyboardButton(text='90085903', callback_data='90085903')]
        keyboard.add(*bots)

        return keyboard
