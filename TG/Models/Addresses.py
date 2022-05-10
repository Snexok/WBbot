from TG.Models.Model import Model

COLUMNS = ["id", "address", "tg_id", "added_to_bot"]


class Address(Model):
    def __init__(self, id=0, address='', tg_id='', added_to_bot=''):
        super().__init__()
        self.id = id
        self.address = address
        self.tg_id = tg_id
        self.added_to_bot = added_to_bot

    def load(self, tg_id=None, address=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM addresses "
        is_where = False
        if tg_id:
            path += "WHERE " if not is_where else ""
            path += "tg_id='" + tg_id + "'"
        if address:
            path += "WHERE " if not is_where else ""
            path += "address='" + address + "'"
        return self.format_data(self.execute(path, callback))

    def update(self):
        if self.changed:
            path = "UPDATE addresses SET "
            path += "added_to_bot=" + ("TRUE" if self.added_to_bot else "FALSE") + " "
            path += "WHERE address='" + self.address + "'"
            Address.execute(path)

    def format_data(self, data):
        data = data[0]
        self.id = data[0]
        self.address = data[1]
        self.tg_id = data[2]
        self.added_to_bot = data[3]

        return self

class Addresses(Model):

    @staticmethod
    def load(tg_id=None, address=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM addresses "
        is_where = False
        if tg_id:
            path += "WHERE " if not is_where else ""
            path += "tg_id='" + tg_id + "'"
        if address:
            path += "WHERE " if not is_where else ""
            path += "address='" + address + "'"
        return Addresses.format_data(Addresses.execute(path, callback))

    @staticmethod
    def insert(address: Address):
        path = "INSERT INTO addresses (id, address, tg_id, added_to_bot) VALUES "
        path += "((SELECT MAX(id)+1 FROM addresses), '" + address.address + "', '" + address.tg_id + "', FALSE)"
        Address.execute(path)

    @staticmethod
    def get_all_not_added():
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM addresses WHERE added_to_bot=FALSE"
        return Addresses.format_data(Addresses.execute(path, callback))

    @staticmethod
    def format_data(data):
        addresses = []
        for d in data:
            address = Address()
            address.id = d[0]
            address.address = d[1]
            address.tg_id = d[2]
            address.added_to_bot = d[3]
            addresses += [address]

        if addresses:
            return addresses
        else:
            return False

    @staticmethod
    def compare_addresses(first_addresses: list, second_addresses: list) -> list:
        comp_adrses = []
        for f_adrs in first_addresses:
            if f_adrs.address not in [s_adrs.address for s_adrs in second_addresses]:
                comp_adrses += [f_adrs]

        for s_adrs in second_addresses:
            if s_adrs.address not in [f_adrs.address for f_adrs in first_addresses]:
                comp_adrses += [s_adrs]

        return comp_adrses