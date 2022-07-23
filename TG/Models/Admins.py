from TG.Models.Model import Model


class Admin_Model(Model):
    COLUMNS = ['id', 'name', 'sentry']
    table_name = 'admins'

    def __init__(self, id=1, name='', sentry=False):
        super().__init__()
        self.id = id
        self.name = name
        self.sentry = sentry


class Admins_Model(Model):
    single_model = Admin_Model
    table_name = single_model.table_name

    @classmethod
    def load(cls, id=None, sentry=None, all=False):
        if all:
            path = f"SELECT * FROM {cls.table_name}"
        elif id:
            path = f"SELECT * FROM {cls.table_name} WHERE id='{id}'"
        elif sentry:
            sentry = "TRUE" if sentry else "FALSE"
            path = f"SELECT * FROM {cls.table_name} WHERE sentry={sentry}"

        data = cls.format_data(cls.execute(path, cls.fetchall))

        if id or sentry:
            return data[0]
        else:
            return data

    @classmethod
    def get_ids(cls):
        path = "SELECT id FROM admins"

        admins = cls.execute(path, cls.fetchall)

        ids = [admin[0] for admin in admins]

        return ids

    @classmethod
    def get_sentry_admin(cls):
        admin = cls.load(sentry=True)
        return admin
