from TG.Models.Model import Model


class Users(Model):

    @staticmethod
    def load(id=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT * FROM users WHERE id='" + id + "'"
        return Users.format_data(Users.execute(path, callback))

    @staticmethod
    def insert(user):
        path = "INSERT INTO users (id, pup_state, name, addresses) VALUES "
        path += "('" + str(user.id) + "', " + str(user.pup_state) + ", '" + user.name + "', ARRAY" + str(
            user.addresses) + "::text[])"
        User.execute(path)

    @staticmethod
    def format_data(data):
        print(data)
        users = []
        for d in data:
            user = User()
            user.id = d[0]
            user.pup_state = d[1]
            user.name = d[2]
            user.addresses = d[3]
            users += [user]

        if users:
            if len(users):
                return users[0]
            return users
        else:
            return False


class User(Model):
    def __init__(self, id='0', pup_state=0, name='', addresses=[]):
        super().__init__()
        self.id = id
        self.pup_state = pup_state
        self.name = name
        self.addresses = addresses

    def update(self):
        if self.changed:
            path = "UPDATE users SET "
            path += "addresses= ARRAY" + str(self.addresses) + "::text[], "
            path += "name= '" + str(self.name) + "', "
            path += "pup_state= " + str(self.pup_state) + " "
            path += "WHERE id='" + str(self.id) + "'"
            User.execute(path)
