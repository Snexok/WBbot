from TG.Models.Model import Model


class User(Model):
    def __init__(self, id='0', name='', addresses=[], username='', role='', cities=[]):
        super().__init__()
        self.id = id
        self.name = name
        self.addresses = addresses
        self.username = username
        self.role = role
        self.cities = cities

    def insert(self):
        path = "INSERT INTO users (id, name, addresses, username, role, cities) VALUES " \
               f"('{str(self.id)}', '{self.name}', ARRAY{str(self.addresses)}::text[], " \
               f"'{self.username}', '{self.role}', ARRAY{str(self.cities)}::text[])"
        User.execute(path)

    def update(self):
        if self.changed:
            path = "UPDATE users SET "
            path += "addresses= ARRAY[" + ",".join(
                "'" + a.replace(",", ";") + "'" for a in self.addresses) + "]::text[], "
            path += f"name= '{self.name}' "
            path += f"WHERE id='{str(self.id)}'"
            User.execute(path)


class Users(Model):

    @classmethod
    def load(cls, id=None, username=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records
        if id:
            path = f"SELECT * FROM users WHERE id='{id}'"
        elif username:
            pass

        return cls.format_data(cls.execute(path, callback))

    @classmethod
    def format_data(cls, data):
        users = []
        for d in data:
            user = User(*d)
            user.addresses = [address.replace(';', ',') for address in user.addresses] if user.addresses else []
            users += [user]

        if users:
            if len(users) == 1:
                return users[0]
            return users
        else:
            return False
