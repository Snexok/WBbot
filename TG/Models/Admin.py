from TG.Models.Model import Model

class Admin(Model):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.sentry = False

    def load(self, id=None, sentry=None):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        if id:
            path = "SELECT * FROM admins WHERE id='" + id + "'"
        elif sentry:
            path = "SELECT * FROM admins WHERE sentry='" + ("TRUE" if sentry else "FALSE") + "'"

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
    @staticmethod
    def load(id=None, sentry=None, all=False):
        def callback(cursor):
            records = cursor.fetchall()
            return records

        if all:
            "SELECT * FROM admins"
        elif id:
            path = "SELECT * FROM admins WHERE id='" + id + "'"
        elif sentry:
            path = "SELECT * FROM admins WHERE sentry='" + ("TRUE" if sentry else "FALSE") + "'"

        return Admins.format_data(Admins.execute(path, callback))

    @staticmethod
    def format_data(data):
        admins = []
        for d in data:
            admin = Admin()
            admin.id = d[0]
            admin.name = d[1]
            admin.sentry = d[2]
            admins += [admin]

        if admins:
            if len(admins) == 1:
                return admins[0]
            return admins
        else:
            return False



