from TG.Models.Model import Model


class Address_Model(Model):
    COLUMNS = ["id", "address", "tg_id", "added_to_bot", "checked"]
    table_name = 'addresses'

    def __init__(self, id=0, address='', tg_id='', added_to_bot=False, checked=False):
        super().__init__()
        self.id = id
        self.address = address
        self.tg_id = tg_id
        self.added_to_bot = added_to_bot
        self.checked = checked


class Addresses_Model(Model):
    single_model = Address_Model
    table_name = single_model.table_name

    @classmethod
    def load(cls, tg_id=None, address=None):
        path = f"SELECT * FROM {cls.table_name} "
        is_where = False
        if tg_id:
            path += "WHERE " if not is_where else ""
            path += f"tg_id='{tg_id}'"
        if address:
            path += "WHERE " if not is_where else ""
            path += f"address='{address}'"

        data = cls.format_data(cls.execute(path, cls.fetchall))

        if tg_id or address:
            return data[0]
        else:
            return data

    @classmethod
    def get_all_not_added(cls):
        path = f"SELECT * FROM {cls.table_name} WHERE added_to_bot=FALSE"
        return cls.format_data(Addresses_Model.execute(path, cls.fetchall))

    @classmethod
    def get_all_not_checked(cls):
        path = f"SELECT * FROM {cls.table_name} WHERE checked=FALSE"
        return cls.format_data(Addresses_Model.execute(path, cls.fetchall))

    @classmethod
    def compare_addresses(cls, first_addresses: list, second_addresses: list) -> list:
        comp_adrses = []
        for f_adrs in first_addresses:
            if f_adrs.address not in [s_adrs.address for s_adrs in second_addresses]:
                comp_adrses += [f_adrs]

        for s_adrs in second_addresses:
            if s_adrs.address not in [f_adrs.address for f_adrs in first_addresses]:
                comp_adrses += [s_adrs]

        return comp_adrses
