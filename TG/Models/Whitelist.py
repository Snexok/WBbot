from TG.Models.Model import Model

COLUMNS = ["id", "tg_id", "username", "secret_key"]


class Whitelist(Model):
    def __init__(self, id=0, tg_id='', username='', secret_key=''):
        super().__init__()
        self.id = id
        self.tg_id = tg_id
        self.username = username
        self.secret_key = secret_key

    def format_data(self, data):
        self.id = data[0]
        self.tg_id = data[1]
        self.username = data[2]
        self.secret_key = data[3]

        return self

    @staticmethod
    def check(tg_id):
        def callback(cursor):
            records = cursor.fetchone()
            return records

        path = "SELECT * FROM whitelist "
        path += "WHERE tg_id='" + tg_id + "' LIMIT 1"

        whitelist = Whitelist.execute(path, callback)

        if whitelist:
            return True
        else:
            return False

    @staticmethod
    def insert(username='', secret_key=''):
        path = "INSERT INTO whitelist (id, tg_id, username, secret_key) VALUES "
        path += "((SELECT MAX(id)+1 FROM whitelist), '', '" + username + "', '" + secret_key + "')"
        Whitelist.execute(path)

    @staticmethod
    def set_secret_key(secret_key):
        Whitelist.insert(secret_key=secret_key)

    @staticmethod
    def set_username(username):
        Whitelist.insert(username=username)

    @staticmethod
    def set_tg_id(tg_id, username='', secret_key=''):
        def callback(cursor):
            return cursor.rowcount

        path = "UPDATE whitelist SET "
        path += "tg_id='" + tg_id + "' "
        if username:
            path += ", username='' "
            path += "WHERE username='" + username + "'"
        elif secret_key:
            path += ", secret_key='' "
            path += "WHERE secret_key='" + secret_key + "'"
        res = Whitelist.execute(path, callback)

        return res