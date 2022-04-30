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
    def insert(data):
        path = "INSERT INTO users (id, pup_state, name, addresses) VALUES "
        path += "('"+str(data.id)+"', "+str(data.pup_state)+", '"+data.name+"', ARRAY"+str(data.addresses)+")"
        Users().execute(path)

    @staticmethod
    def update(user):
        path = "UPDATE users SET "
        # path += "address='" + address.address +"', "
        if len(user.addresses):
            path += "addresses= addresses || ARRAY"+str(user.addresses)+" "
        path += "pup_state= " + str(user.pup_state) + " "
        path += "WHERE id='" + str(user.id) + "'"
        Users().execute(path)

    @staticmethod
    def get_all_not_added():
        def callback(cursor):
            records = cursor.fetchall()
            return records
        path = "SELECT * FROM addresses WHERE added_to_bot=FALSE"
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

class User:
    def __init__(self, id='0', pup_state=0, name='', addresses=[]):
        self.id = id
        self.pup_state = pup_state
        self.name = name
        self.addresses = addresses

Users().insert(User('1234', 0, 'WAD', ['1', '2', '3']))
