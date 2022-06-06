from TG.Models.Model import Model

COLUMNS = ["id", "tg_id", "username", "secret_key"]


class Whitelist(Model):
    def __init__(self, id=0, tg_id='', username='', secret_key=''):
        super().__init__()
        self.id = id
        self.tg_id = tg_id
        self.username = username
        self.secret_key = secret_key

    def insert(self):
        path = "INSERT INTO whitelist (id, tg_id, username, secret_key) VALUES "
        path += f"((SELECT MAX(id)+1 FROM whitelist), '', '{self.username}', '{self.secret_key}')"
        self.execute(path)

    def format_data(self, data):
        self.id = data[0]
        self.tg_id = data[1]
        self.username = data[2]
        self.secret_key = data[3]

        return self

    @classmethod
    def check(cls, tg_id):
        def callback(cursor):
            records = cursor.fetchone()
            return records

        path = "SELECT * FROM whitelist "
        path += f"WHERE tg_id='{tg_id}' LIMIT 1"

        whitelist = cls.execute(path, callback)

        if whitelist:
            return True
        else:
            return False


    @classmethod
    def set_tg_id(cls, tg_id, username='', secret_key=''):
        def callback(cursor):
            return cursor.rowcount

        path = "UPDATE whitelist SET "
        path += f"tg_id='{tg_id}' "
        if username:
            path += ", username='' "
            path += f"WHERE username='{username}'"
        elif secret_key:
            path += ", secret_key='' "
            path += f"WHERE secret_key='{secret_key}'"
        res = cls.execute(path, callback)

        return res
