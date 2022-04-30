from TG.Models.Model import Model

class Users(Model):

    @staticmethod
    def load(id=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records
        path = "SELECT * FROM users WHERE id='" + id + "'"
        return Users().format_data(Users().execute(path, callback))

    @staticmethod
    def format_data(data):
        users = []
        for d in data:
            user = User()
            user.id = d[0]
            user.pup_state = d[1]
            user.name = d[2]
            user.addresses = d[3]

        if users:
            if len(users):
                return users[0]
            return users
        else:
            return False

class User(Model):
    def __init__(self, id='0', pup_state=0, name='', addresses=[]):
        self.id = id
        self.pup_state = pup_state
        self.name = name
        self.addresses = addresses
        self.changed = False

    def insert(self, data):
        path = "INSERT INTO users (id, pup_state, name, addresses) VALUES "
        path += "('"+str(data.id)+"', "+str(data.pup_state)+", '"+data.name+"', ARRAY"+str(data.addresses)+")"
        User.execute(path)

    def update(self):
        if self.changed:
            path = "UPDATE users SET "
            path += "addresses= ARRAY" + str(self.addresses) + " "
            path += "pup_state= " + str(self.pup_state) + " "
            path += "WHERE id='" + str(self.id) + "'"
            Users().execute(path)

    def append(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, getattr(self, k)+v)

    def set(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
