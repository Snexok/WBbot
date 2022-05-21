from TG.Models.Model import Model

class Admin(Model):
    def __init__(self, id=0, name='', sentry=False):
        self.id = id
        self.name = name
        self.sentry = sentry

    def load(self, id=None, sentry=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        if id:
            path = f"SELECT * FROM admins WHERE id='{id}'"
        elif sentry:
            sentry = "TRUE" if sentry else "FALSE"
            path = f"SELECT * FROM admins WHERE sentry={sentry}"

        self.set_data(self.execute(path, callback))
        return self

    def set_data(self, data):
        for d in data:
            self.id = d[0]
            self.name = d[1]
            self.sentry = d[2]

    def get_sentry_admin(self):
        self.load(sentry=True)
        return self



class Admins(Model):
    @classmethod
    def load(cls, id=None, sentry=None, all=False):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        if all:
            path = "SELECT * FROM admins"
        elif id:
            path = f"SELECT * FROM admins WHERE id='{id}'"
        elif sentry:
            sentry = "TRUE" if sentry else "FALSE"
            path = f"SELECT * FROM admins WHERE sentry={sentry}"

        return cls.format_data(cls.execute(path, callback))

    @classmethod
    def format_data(cls, data):
        admins = []
        for d in data:
            admin = Admin(*d)
            admins += [admin]

        if admins:
            return admins
        else:
            return False

    @classmethod
    def get_ids(cls):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        path = "SELECT id FROM admins"
        ids = cls.execute(path, callback)
        return [id[0] for id in ids]