from TG.Models.Model import Model


class User(Model):
    COLUMNS = ['id', 'name', 'addresses', 'username', 'role', 'cities', 'inn', 'ie']
    table_name = 'users'

    def __init__(self, id='0', name='', addresses=[], username='', role='', cities=[], inn='', ie=''):
        super().__init__()
        self.id = id
        self.name = name
        self.addresses = addresses
        self.username = username
        self.role = role
        self.cities = cities
        self.inn = inn
        self.ie = ie

class Users(Model):
    single_model = User
    table_name = single_model.table_name

    @classmethod
    def load(cls, id=None, username=None, role=None, inn=None, ie=None):
        if id:
            path = f"SELECT * FROM {cls.table_name} WHERE id='{id}'"
        elif username:
            pass
        elif role:
            path = f"SELECT * FROM {cls.table_name} WHERE role='{role}'"
        elif inn:
            path = f"SELECT * FROM {cls.table_name} WHERE inn='{inn}'"
        elif ie:
            path = f"SELECT * FROM {cls.table_name} WHERE ie='{ie}'"

        data = cls.format_data(cls.execute(path, cls.fetchall))

        if id or username or inn or ie:
            return data[0]
        return data

    @classmethod
    def format_data(cls, data):
        users = []
        for d in data:
            user = cls.single_model(*d)
            user.addresses = [address.replace(';', ',') for address in user.addresses] if user.addresses else []
            users += [user]

        if users:
            return users
        else:
            return False
