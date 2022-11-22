import pymysql


class SQLighter:

    def __init__(self, database_link):
        db_link = database_link
        s = db_link.split("mysql://")[1].split(':')
        db_settings = self.get_parsed_url(s)
        self.connection = self.connect_to_db(db_settings)
        self.cursor = self.connection.cursor()

    def check_connection(f):
        def wrapper(*args):
            args[0].connection.ping(reconnect=True)
            return f(*args)
        return wrapper

    def connect_to_db(self, db_settings):
        try:
            connection = pymysql.connect(
                host=db_settings['host'],
                port=db_settings['port'],
                user=db_settings['user'],
                password=db_settings['password'],
                database=db_settings['database'],
                cursorclass=db_settings['cursorclass'],
            )

        except Exception as ex:
            print(ex)
        else:
            return connection

    def get_parsed_url(self, s: list) -> dict:
        if type(s) != list:
            return -1
        data = {}
        data['user'] = s[0]
        data['password'] = s[1].split('@')[0]
        data['host'] = s[1].split('@')[1]
        data['port'] = int(s[2].split('/')[0])
        data['database'] = s[2].split('/')[1]
        data['cursorclass'] = pymysql.cursors.DictCursor
        return data

    def close(self):
        self.connection.close()

    @check_connection
    def commit(self):
        self.connection.commit()
