from aiogram.dispatcher.filters.state import StatesGroup, State


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
    PLAN_BOT_SEARCH = State()
    BOT_BUY = State()
    COLLECT_OTHER_ORDERS = State()
    EXCEPTED_ORDERS_LIST = State()
    EXCEPTED_ORDERS_LIST_CHANGE = State()
    COLLECT_ORDERS = State()
    AUTH_PARTNER = State()
    CREATE_ORDER = State()
    WATCH_ORDER = State()
    RE_BUY = State()
