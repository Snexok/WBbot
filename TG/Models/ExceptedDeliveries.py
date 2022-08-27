from datetime import datetime

from TG.Models.Model import Model


class ExceptedDelivery_Model(Model):
    COLUMNS = ['id', 'inn', 'delivery_number', 'start_datetime']
    table_name = 'excepted_deliveries'

    def __init__(self, id=1, inn='', delivery_number='', start_datetime=''):
        super().__init__()
        self.id = id
        self.inn = inn
        self.delivery_number = delivery_number
        self.start_datetime = start_datetime


class ExceptedDeliveries_Model(Model):
    single_model = ExceptedDelivery_Model
    table_name = single_model.table_name

    @classmethod
    def load(cls, inn=None):
        path = f"SELECT * FROM {cls.table_name}"
        if inn:
            path += f" WHERE inn='{inn}' AND "

            path = path[:-5]

        return cls.format_data(cls.execute(path, cls.fetchall))
