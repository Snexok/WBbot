from TG.Models.Model import Model

COLUMNS = ["id", "address", "tg_id", "added_to_bot", "checked"]


class Address(Model):
    def __init__(self, id=0, address='', tg_id='', added_to_bot=False, checked=False):
        super().__init__()
        self.id = id
        self.address = address
        self.tg_id = tg_id
        self.added_to_bot = added_to_bot
        self.checked = checked

    def load(self, tg_id=None, address=None):
        path = "SELECT * FROM addresses "
        is_where = False
        if tg_id:
            path += "WHERE " if not is_where else ""
            path += f"tg_id='{tg_id}'"
        if address:
            path += "WHERE " if not is_where else ""
            path += f"address='{address}'"
        return self.format_data(self.execute(path, self.fetchall))

    def update(self):
        if self.changed:
            path = "UPDATE addresses SET "
            added_to_bot = "TRUE" if self.added_to_bot else "FALSE"
            path += f"added_to_bot={added_to_bot} AND "
            checked = "TRUE" if self.checked else "FALSE"
            path += f"checked={checked} "
            path += f"WHERE address='{self.address}'"
            Address.execute(path)

    def format_data(self, data):
        data = data[0]
        self.id = data[0]
        self.address = data[1]
        self.tg_id = data[2]
        self.added_to_bot = data[3]
        self.checked = data[4]

        return self

class Addresses(Model):

    @classmethod
    def load(cls, tg_id=None, address=None):
        path = "SELECT * FROM addresses "
        is_where = False
        if tg_id:
            path += "WHERE " if not is_where else ""
            path += f"tg_id='{tg_id}'"
        if address:
            path += "WHERE " if not is_where else ""
            path += f"address='{address}'"
        return cls.format_data(cls.execute(path, cls.fetchall))

    @classmethod
    def insert(cls, address: Address):
        path = "INSERT INTO addresses (id, address, tg_id, added_to_bot, checked) VALUES "
        path += f"((SELECT MAX(id)+1 FROM addresses), '{address.address}', '{address.tg_id}', FALSE, FALSE)"
        cls.execute(path)

    @classmethod
    def get_all_not_added(cls):
        path = "SELECT * FROM addresses WHERE added_to_bot=FALSE"
        return cls.format_data(Addresses.execute(path, cls.fetchall))

    @classmethod
    def get_all_not_checked(cls):
        path = "SELECT * FROM addresses WHERE checked=FALSE"
        return cls.format_data(Addresses.execute(path, cls.fetchall))

    @classmethod
    def format_data(cls, data):
        addresses = []
        for d in data:
            address = Address()
            address.id = d[0]
            address.address = d[1]
            address.tg_id = d[2]
            address.added_to_bot = d[3]
            address.checked = d[4]
            addresses += [address]

        if addresses:
            return addresses
        else:
            return False

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