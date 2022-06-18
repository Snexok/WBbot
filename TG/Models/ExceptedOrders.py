from datetime import datetime

from TG.Models.Model import Model


class ExceptedOrder(Model):
    COLUMNS = ['id', 'inn', 'order_number', 'start_datetime']
    table_name = 'excepted_orders'

    def __init__(self, id=1, inn='', order_number='', start_datetime=''):
        super().__init__()
        self.id = id
        self.inn = inn
        self.order_number = order_number
        self.start_datetime = start_datetime


class ExceptedOrders(Model):
    single_model = ExceptedOrder
    table_name = single_model.table_name

    @classmethod
    def load(cls, inn=None):
        path = f"SELECT * FROM {cls.table_name}"
        if inn:
            path += f" WHERE inn='{inn}', "

        path = path[:-2]

        return cls.format_data(cls.execute(path, cls.fetchall))

    @classmethod
    def delete(cls, order_number):
        path = f"DELETE FROM {cls.table_name} WHERE order_number='{order_number}'"

        return cls.execute(path)
