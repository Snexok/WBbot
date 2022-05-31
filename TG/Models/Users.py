from TG.Models.Model import Model


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
    def insert(cls, user):
        path = "INSERT INTO users (id, pup_state, name, addresses, username) VALUES "
        path += f"('{str(user.id)}', {str(user.pup_state)}, '{user.name}', ARRAY{str(user.addresses)}::text[], '{str(user.username)}')"
        User.execute(path)

    @classmethod
    def format_data(cls, data):
        print(data)
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


class User(Model):
    def __init__(self, id='0', pup_state=0, name='', addresses=[], username=''):
        super().__init__()
        self.id = id
        self.pup_state = pup_state
        self.name = name
        self.addresses = addresses
        self.username = username

    def update(self):
        if self.changed:
            path = "UPDATE users SET "
            path += "addresses= ARRAY[" + ",".join(
                "'" + a.replace(",", ";") + "'" for a in self.addresses) + "]::text[], "
            path += f"name= '{str(self.name)}', "
            path += f"pup_state= {str(self.pup_state)} "
            path += f"WHERE id='{str(self.id)}'"
            User.execute(path)
