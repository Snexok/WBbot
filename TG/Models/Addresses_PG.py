from TG.Models.Model import Model

COLUMNS = ["id", "address", "tg_id", "added_to_bot"]

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
        return Addresses().format_data(Addresses().execute(path, callback))

    @staticmethod
    def insert(data):
        path = "INSERT INTO addresses (id, address, tg_id, added_to_bot) VALUES "
        path += "((SELECT MAX(id)+1 FROM addresses), '"+data.address+"', '"+data.tg_id+"', FALSE)"
        Addresses().execute(path)

    @staticmethod
    def update(address):
        path = "UPDATE addresses SET "
        # path += "address='" + address.address +"', "
        path += "added_to_bot=" + "TRUE" if address.added_to_bot else "FALSE" + " "
        path += "WHERE address='" + address.address + "'"
        Addresses().execute(path)

    @staticmethod
    def get_all_not_added():
        def callback(cursor):
            records = cursor.fetchall()
            return records
        path = "SELECT * FROM addresses WHERE added_to_bot=FALSE"
        return Addresses().format_data(Addresses().execute(path, callback))

    @staticmethod
    def format_data(data):
        addresses = []
        for d in data:
            address = Address()
            address.id = d[0]
            address.address = d[1]
            address.tg_id = d[2]
            address.added_to_bot = d[3]

        if addresses:
            return addresses
        else:
            return False

class Address:
    def __init__(self, id=0, address='', tg_id='', added_to_bot=''):
        self.id = id
        self.address = address
        self.tg_id = tg_id
        self.added_to_bot = added_to_bot
