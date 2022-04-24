# Consts
import TG.CONSTS.STATES as STATES

# For telegram api
# pip install python-telegram-bot --upgrade
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
        CallbackQueryHandler, TypeHandler, ConversationHandler

from TG.Admin import Admin
from TG.Models.User import User
from TG.PUP import PUP
from configs import config


# Commands
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет")


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def main_handler(update: Update, context: CallbackContext):
    # DEV
    id = str(update.effective_user.id)
    user = User.load(id)
    user['pup_state'] = 0
    User.save(user)
    # DEV

    msg = update.message.text.lower()
    if "пвз" in msg:
        update.message.reply_text("Ваше ФИО?")
        return STATES['PUP']
    elif "заказ" in msg:
        reply_keyboard = [
            ['Файл', 'Чат'],
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        update.message.reply_text('Файлом или через чат?', reply_markup=markup)

        return STATES['ORDER']
    return STATES['MAIN']


def order_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    answer = query.data
    if answer == "Файл":
        pass
        # run_by_doc(update, context)
    elif answer == 'Чат':
        pass

    return STATES['MAIN']


def order_handler(update: Update, context: CallbackContext):
    pass


def main() -> None:
    updater = Updater(config['tokens']['telegram'])
    admin = Admin()
    pup = PUP()
    dispatcher = updater.dispatcher

    dispatcher.add_handler(TypeHandler(Update, User.track_handler), group=-1)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('Admin'), admin.handler),
                      MessageHandler(Filters.text & ~Filters.command, main_handler)],
        states={
            STATES['ADMIN']: [
                MessageHandler(Filters.regex('Admin'), admin.handler),
                MessageHandler(Filters.text, admin.handler)
            ],
            STATES['MAIN']: [
                MessageHandler(Filters.regex('Admin'), admin.handler),
                MessageHandler(Filters.text, main_handler)
            ],
            STATES['ORDER']: [
                CallbackQueryHandler(order_callback_handler),
                MessageHandler(Filters.text, order_handler)
            ],
            STATES['PVZ']: [
                MessageHandler(Filters.text, main_handler)
            ],
            STATES['INSIDE']: [
                MessageHandler(Filters.document, admin.inside_handler)
            ],
            STATES['PUP']: [
                MessageHandler(Filters.text, pup.handler)
            ],
            STATES['ADMIN_ADDRESS_DISTRIBUTION']: [
                MessageHandler(Filters.text, admin.address_distribution_handler)
            ],

        },
        fallbacks=[CommandHandler("start", start)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
