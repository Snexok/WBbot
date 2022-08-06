from TG.Models.Model import Model


class Whitelist_Model(Model):
    COLUMNS = ["id", "tg_id", "username", "secret_key"]
    table_name = 'whitelist'

    def __init__(self, id=1, tg_id='', username='', secret_key=''):
        super().__init__()
        self.id = id
        self.tg_id = tg_id
        self.username = username
        self.secret_key = secret_key

    @classmethod
    def check(cls, tg_id):
        path = f"SELECT * FROM {cls.table_name} WHERE tg_id='{tg_id}' LIMIT 1"

        whitelist = cls.execute(path, cls.fetchall)

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
