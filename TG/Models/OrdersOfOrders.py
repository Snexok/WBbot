from datetime import datetime

from TG.Models.Model import Model

class OrderOfOrders_Model(Model):
    COLUMNS = ['id', 'inn', 'articles', 'active', 'quantities_to_bought', 'quantities_bought', 'search_keys',
               'numbers_of_comments', 'comments', 'unused_comments', 'left_comments', 'bought_per_day', 'budget',
               'remaining_budget', 'start_datetime', 'end_datetime']
    table_name = 'orders_of_orders'

    def __init__(self, id=1, inn='', articles=[], active=[], quantities_to_bought=0, quantities_bought=[], search_keys=[],
                 numbers_of_comments=[], comments=[], unused_comments=[], left_comments=[], bought_per_day=0, budget=0, remaining_budget=0,
                 start_datetime='', end_datetime=''):
        super().__init__()
        self.id = id
        self.inn = inn
        self.articles = articles
        self.active = active if active else [True for _ in range(len(articles))]
        self.quantities_to_bought = quantities_to_bought
        self.quantities_bought = quantities_bought if quantities_bought else [0 for _ in range(len(quantities_to_bought))]
        self.search_keys = search_keys
        self.numbers_of_comments = numbers_of_comments
        self.comments = comments
        self.unused_comments = unused_comments if unused_comments else comments
        self.left_comments = left_comments
        self.bought_per_day = bought_per_day
        self.budget = budget
        self.remaining_budget = remaining_budget
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

class OrdersOfOrders_Model(Model):
    single_model = OrderOfOrders_Model
    table_name = single_model.table_name

    @classmethod
    def load(cls, id=None, inn=None):
        path = f"SELECT * FROM {cls.table_name} WHERE end_datetime is null AND "
        if inn:
            path += f" inn='{inn}' AND "
        if id:
            path += f" id='{id}' AND "

        path = path[:-5]

        data = cls.format_data(cls.execute(path, cls.fetchall))

        if id:
            data = data[0]

        return data
