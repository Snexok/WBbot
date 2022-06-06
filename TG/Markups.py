from aiogram import types


def get_markup(markup_name, role='', is_admin=False, id='', *args):
    if 'pup_addresses' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Всё")

        return markup
    elif 'admin_main' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Добавить пользователя")
        markup.add("Сделать выкуп")
        if id:
            if id == '794329884' or id == '535533975':
                markup.add("Открыть бота")
                markup.add("Проверить ожидаемое")
        markup.add("Проверить ботов")
        markup.add("Назад")

        return markup
    elif 'main_order' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Файл")
        markup.add("Чат")

        return markup
    elif 'admin_add_user' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("По username")
        markup.add("Сгененрировать ключ")

        return markup
    elif 'main_main' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        if is_admin:
            markup.add("Admin")
        if role in "FF":
            markup.add("Собрать выкупы")
            markup.add("Собрать РЕАЛЬНЫЕ заказы")
        markup.add("Регистрация")
        # markup.add("Настройки")

        return markup
    elif 'main_register' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Как ПВЗ")
        markup.add("Как ФФ")
        # markup.add("Для выкупов")

        return markup
    elif 'admin_bots' == markup_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        bots_name = args[0]
        for bot_name in bots_name:
            markup.add(bot_name)

        return markup
    elif '' == markup_name:
        pass
    elif '' == markup_name:
        pass