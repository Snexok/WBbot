from TG.Models.Model import Model


class User_Model(Model):
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

    def insert(self):
        c = [col for col in self.COLUMNS if getattr(self, col) or type(getattr(self, col)) is bool]
        path = f"INSERT INTO {self.table_name} (" + ", ".join(c) + ") VALUES "
        path += f"({self.id}, "
        for k in self.COLUMNS[1:]:
            v = getattr(self, k)
            if v or type(v) is bool:
                if type(v) is int:
                    path += f"{str(v)}, "
                elif type(v) is str:
                    path += f"'{str(v)}', "
                elif type(v) is bool:
                    v = "TRUE" if v else "FALSE"
                    path += f"{v}, "
                elif type(v) is list:
                    if type(v[0]) is str:
                        if "," in str(v):
                            path += "ARRAY[" + ",".join("'" + a.replace(",", ";") + "'" for a in v) + "]::text[], "
                        else:
                            path += f"ARRAY{str(v)}::text[], "
                    elif type(v[0]) is int:
                        path += f"ARRAY{str(v)}::integer[], "
        path = path[:-2]
        path += ")"
        print(path)
        self.execute(path)

class Users_Model(Model):
    single_model = User_Model
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
            if data:
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
