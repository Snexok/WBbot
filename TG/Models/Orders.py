from TG.Models.Model import Model

COLUMNS = ['id', 'number', 'total_price', 'services_price', 'prices', 'quantities', 'articles', 'statuses',
           'pup_address', 'pup_tg_id', 'bot_name', 'bot_surname', 'start_date', 'pred_end_date', 'end_date',
           'code_for_approve', 'active']


class Orders(Model):

    @staticmethod
    def load(number=None, bot_name=None, articles=None, address=None, active=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM orders WHERE "
        if number:
            path += "number = " + str(number) + ", "
        if bot_name:
            path += "bot_name = '" + str(bot_name) + "', "
        if articles:
            path += "articles = ARRAY" + str(articles) + "::text[], "
        if address:
            path += "address = '" + str(address) + "', "
        if active:
            path += "active = " + ("TRUE" if active else "FALSE") + ", "

        path = path[:-2]

        return Orders.format_data(Orders.execute(path, callback))

    @staticmethod
    def format_data(data):
        orders = []
        for d in data:
            order = Order(*d)
            orders += [order]

        if orders:
            if len(orders) == 1:
                return orders[0]
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
    def __init__(self, id=1, number=0, total_price=0, services_price=0, prices=[], quantities=[], articles=[],
                 statuses=[], pup_address='', pup_tg_id='', bot_name='', bot_surname='', start_date='',
                 pred_end_date='', end_date='', code_for_approve='', active=True):
        super().__init__()
        self.id = id
        self.number = number
        self.total_price = total_price
        self.services_price = services_price
        self.prices = prices
        self.quantities = quantities
        self.statuses = statuses
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

    def __str__(self):
        res = ""
        for i, col in enumerate(COLUMNS):
            res += col + " = " + str(getattr(self, col)) + "; "
        return res

    def __dict__(self):
        return {'id': self.id, 'number': self.number, 'total_price': self.total_price, 'services_price': self.services_price,
         'prices': self.prices, 'quantities': self.quantities, 'statuses': self.statuses, 'articles': self.articles,
         'pup_address': self.pup_address, 'pup_tg_id': self.pup_tg_id, 'bot_name': self.bot_name,
         'bot_surname': self.bot_surname, 'start_date': self.start_date, 'pred_end_date': self.pred_end_date,
         'end_date': self.end_date, 'code_for_approve': self.code_for_approve, 'active': self.active}

    def insert(self):
        c = [col for col in COLUMNS if getattr(self, col)]
        path = "INSERT INTO orders (" + ", ".join(c) + ") VALUES "
        path += "((SELECT MAX(id)+1 FROM orders), "
        for k in COLUMNS[1:]:
            v = getattr(self, k)
            if v:
                if type(v) is int:
                    path += str(v) + ", "
                elif type(v) is str:
                    path += "'" + str(v) + "', "
                elif type(v) is bool:
                    path += ("TRUE" if v else "FALSE") + ", "
                elif type(v) is list:
                    if type(v[0]) is str:
                        path += "ARRAY" + str(v) + "::text[], "
                    elif type(v[0]) is int:
                        path += "ARRAY" + str(v) + "::integer[], "
        path = path[:-2]
        path += ")"
        print(path)
        Order.execute(path)

    def update(self):
        if self.changed:
            path = "UPDATE orders SET "
            path += "addresses= ARRAY" + str(self.addresses) + "::text[] "
            path += "WHERE name='" + str(self.name) + "'"
            Order.execute(path)
