import datetime

from TG.Models.Model import Model

COLUMNS = ['id', 'number', 'total_price', 'services_price', 'prices', 'quantities', 'articles',
           'pup_address', 'pup_tg_id', 'bot_name', 'bot_surname', 'start_date', 'pred_end_date', 'end_date',
           'code_for_approve', 'active', 'statuses']


class Orders(Model):

    @staticmethod
    def load(number=None, bot_name=None, articles=None, pup_address=None, active=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM orders WHERE "
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

        path = path[:-5]

        print(path)
        orders = Orders.format_data(Orders.execute(path, callback))
        print(orders)
        return orders

    @staticmethod
    def format_data(data):
        orders = []
        for d in data:
            order = Order(*d)
            print(*d)
            orders += [order]

        if orders:
            return orders
        else:
            return False

    @staticmethod
    async def get_number():
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT MAX(number)+1 FROM orders"
        res = Orders.execute(path, callback)
        res = res[0][0]
        return res


class Order(Model):
    def __init__(self, id=1, number=0, total_price=0, services_price=0, prices=[], quantities=[], articles=[], pup_address='', pup_tg_id='', bot_name='', bot_surname='', start_date='',
                 pred_end_date='', end_date='', code_for_approve='', active=True,
                 statuses=[]):
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

    def __str__(self):
        res = ""
        for i, col in enumerate(COLUMNS):
            res += col + " = " + str(getattr(self, col)) + "; "
        return res

    def __dict__(self):
        return {'id': self.id, 'number': self.number, 'total_price': self.total_price, 'services_price': self.services_price,
         'prices': self.prices, 'quantities': self.quantities, 'articles': self.articles,
         'pup_address': self.pup_address, 'pup_tg_id': self.pup_tg_id, 'bot_name': self.bot_name,
         'bot_surname': self.bot_surname, 'start_date': self.start_date, 'pred_end_date': self.pred_end_date,
         'end_date': self.end_date, 'code_for_approve': self.code_for_approve, 'active': self.active, 'statuses': self.statuses}

    def insert(self):
        c = [col for col in COLUMNS if getattr(self, col)]
        path = "INSERT INTO orders (" + ", ".join(c) + ") VALUES "
        path += "((SELECT MAX(id)+1 FROM orders), "
        for k in COLUMNS[1:]:
            v = getattr(self, k)
            if v:
                if type(v) is int:
                    path += f"{str(v)}, "
                elif type(v) is str:
                    path += f"'{str(v)}', "
                elif type(v) is bool:
                    v = "TRUE" if v else "FALSE"
                    path += f"{v}, "
                elif type(v) is list:
                    if type(v[0]) is str:
                        path += f"ARRAY{str(v)}::text[], "
                    elif type(v[0]) is int:
                        path += f"ARRAY{str(v)}::integer[], "
        path = path[:-2]
        path += ")"
        self.execute(path)

    def update(self):
        if self.changed:
            path = "UPDATE orders SET "
            for key in COLUMNS[1:]:
                value = getattr(self, key)
                print(key, value, type(value))
                if value or type(value) is bool:
                    if type(value) is int:
                        path += f"{key} = { str(value)}, "
                    elif type(value) is str:
                        path += f"{key} = '{str(value)}', "
                    elif type(value) is datetime.date:
                        path += f"{key} = '{str(value)}', "
                    elif type(value) is bool:
                        value = "TRUE" if value else "FALSE"
                        path += f"{key} = {value}, "
                    elif type(value) is list:
                        if type(value[0]) is str:
                            path += f"{key} = ARRAY{str(value)}::text[], "
                        elif type(value[0]) is int:
                            path += f"{key} = ARRAY{str(value)}::integer[], "
            path = path[:-2]
            path += f" WHERE id='{str(self.id)}'"
            self.execute(path)
