from datetime import datetime

from TG.Models.Model import Model


class Order(Model):
    COLUMNS = ['id', 'number', 'total_price', 'services_price', 'prices', 'quantities', 'articles',
               'pup_address', 'pup_tg_id', 'bot_name', 'bot_surname', 'start_date', 'pred_end_date', 'end_date',
               'code_for_approve', 'active', 'statuses', 'inn', 'collected']
    table_name = 'orders'

    def __init__(self, id=1, number=0, total_price=0, services_price=0, prices=[], quantities=[], articles=[],
                 pup_address='', pup_tg_id='', bot_name='', bot_surname='', start_date='', pred_end_date='',
                 end_date='', code_for_approve='', active=True, statuses=[], inn=[], collected=False):
        super().__init__()
        self.id = id
        self.number = number
        self.total_price = total_price
        self.services_price = services_price
        self.prices = prices
        self.quantities = quantities
        self.articles = articles
        self.pup_address = pup_address
        self.pup_tg_id = pup_tg_id
        self.bot_name = bot_name
        self.bot_surname = bot_surname
        self.start_date = start_date
        self.pred_end_date = pred_end_date
        self.end_date = end_date
        self.code_for_approve = code_for_approve
        self.active = active
        self.statuses = statuses
        self.inn = inn
        self.collected = collected

    def __dict__(self):
        return {'id': self.id, 'number': self.number, 'total_price': self.total_price,
                'services_price': self.services_price,
                'prices': self.prices, 'quantities': self.quantities, 'articles': self.articles,
                'pup_address': self.pup_address, 'pup_tg_id': self.pup_tg_id, 'bot_name': self.bot_name,
                'bot_surname': self.bot_surname, 'start_date': self.start_date, 'pred_end_date': self.pred_end_date,
                'end_date': self.end_date, 'code_for_approve': self.code_for_approve, 'active': self.active,
                'statuses': self.statuses, 'inn': self.inn, 'collected': self.collected}


class Orders(Model):
    single_model = Order
    table_name = single_model.table_name

    @classmethod
    def load(cls, number=None, bot_name=None, articles=None, pup_address=None, active=None, collected=None,
             pred_end_date=None):

        path = f"SELECT * FROM {cls.table_name} WHERE "
        if number:
            path += f"number = {str(number)} AND "
        if bot_name:
            path += f"bot_name = '{str(bot_name)}' AND "
        if articles:
            path += f"articles = ARRAY{str(articles)}::text[] AND "
        if pup_address:
            path += f"pup_address = '{str(pup_address)}' AND "
        if active:
            active = "TRUE" if active else "FALSE"
            path += f"active = {active} AND "
        if collected is not None:
            collected = "TRUE" if collected else "FALSE"
            path += f"collected = {collected} AND "
        if pred_end_date:
            path += f"pred_end_date < '{str(pred_end_date)}' AND "

        path = path[:-5]

        print(path)
        orders = cls.format_data(cls.execute(path, cls.fetchall))

        return orders

    @classmethod
    def get_number(cls):
        path = f"SELECT MAX(number)+1 FROM {cls.table_name}"
        res = cls.execute(path, cls.fetchall)
        res = res[0][0]
        return res
