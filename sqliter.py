import sqlite3
import pymysql


def get_parsed_url(s: list) -> dict:
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

class SQLighter:
    def __init__(self,database_link):
        db_link = database_link
        s = db_link.split("mysql://")[1].split(':')
        db_settings = get_parsed_url(s)
        self.connection = self.connect_to_db(db_settings)
        self.cursor = self.connection.cursor()

    def connect_to_db(self, db_settings):
        try:
            connection = pymysql.connect(
                host = db_settings['host'],
                port = db_settings['port'],
                user = db_settings['user'],
                password = db_settings['password'],
                database = db_settings['database'],
                cursorclass = db_settings['cursorclass'],
                )

        except Exception as ex:
            print(ex)
        else:
            return connection

    def get_users_nicknames(self):
        self.cursor.execute("SELECT username, user_id FROM subscriptions")
        result = [tuple(user.values()) for user in self.cursor.fetchall()]
        result = [user for user in result if user[0] != None and user[1] != None]
        return result

    def user_exists(self,user_id):
        self.cursor.execute(f"SELECT * FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchall()
        return bool(len(result))

    def check_if_admin(self, user_id):
        self.cursor.execute(f"SELECT isAdmin FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        result = bool(result['isAdmin']) if result is not None else False
        return result

    def account_exists(self,user_id):
        self.cursor.execute(f"SELECT hasAccount FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        result = bool(result['hasAccount']) if result is not None else False
        return result

    def get_username(self, user_id):
        self.cursor.execute(f"SELECT username FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        result = result['username'] if result is not None else False
        return result

    def get_password(self, user_id):
        self.cursor.execute(f"SELECT password FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        result = result['password'] if result is not None else False
        return result
        

    def add_user(self,user_id):
        self.cursor.execute(f"INSERT INTO subscriptions (user_id) VALUES ({user_id})")
        self.commit()

    def add_username(self,user_id,username):
        self.cursor.execute(f"UPDATE subscriptions SET username = '{username}' WHERE user_id = {user_id}")

    def add_password(self,user_id,password):
        self.cursor.execute(f"UPDATE subscriptions SET password = {password} WHERE user_id = {user_id}")

    def add_account(self,user_id):
        self.cursor.execute(f"UPDATE subscriptions SET hasAccount = {True} WHERE user_id = {user_id}")
        self.commit()

    def delete_user(self,user_id):
        self.cursor.execute(f"DELETE FROM subscriptions WHERE user_id = {user_id}")

    def close(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()


def main():
    pass

if __name__ == '__main__':
    main()
