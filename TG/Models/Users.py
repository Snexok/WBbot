from TG.Models.Model import Model


class Users(Model):

    @staticmethod
    def load(id=None, username=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records
        if id:
            path = "SELECT * FROM users WHERE id='" + id + "'"
        elif username:
            pass

        return Users.format_data(Users.execute(path, callback))

    @staticmethod
    def insert(user):
        path = "INSERT INTO users (id, pup_state, name, addresses, username) VALUES "
        path += "('" + str(user.id) + "', " + str(user.pup_state) + ", '" + user.name + "', ARRAY" + str(
            user.addresses) + "::text[], '"+str(user.username)+"')"
        print(path)
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
            user.username = d[4]
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
            path += "addresses= ARRAY" + str(self.addresses) + "::text[], "
            path += "name= '" + str(self.name) + "', "
            path += "pup_state= " + str(self.pup_state) + " "
            path += "WHERE id='" + str(self.id) + "'"
            User.execute(path)
