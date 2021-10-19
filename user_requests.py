from sqliter import SQLighter




class User_SQLighter(SQLighter):
    def __init__(self,database_link):
        super().__init__(database_link)

    @SQLighter.check_connection
    def get_users_nicknames(self):
        self.cursor.execute("SELECT username, user_id FROM subscriptions")
        result = [tuple(user.values()) for user in self.cursor.fetchall()]
        result = [user for user in result if user[0] != None and user[1] != None]
        return result


    @SQLighter.check_connection
    def user_exists(self,user_id):
        self.cursor.execute(f"SELECT * FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchall()
        return bool(len(result))


    @SQLighter.check_connection
    def check_if_admin(self, user_id):
        self.cursor.execute(f"SELECT isAdmin FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        result = bool(result['isAdmin']) if result is not None else False
        return result


    @SQLighter.check_connection
    def account_exists(self,user_id):
        self.cursor.execute(f"SELECT hasAccount FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        result = bool(result['hasAccount']) if result is not None else False
        return result



    @SQLighter.check_connection
    def get_username(self, user_id):
        self.cursor.execute(f"SELECT username FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        result = result['username'] if result is not None else False
        return result


    @SQLighter.check_connection
    def get_password(self, user_id):
        self.cursor.execute(f"SELECT password FROM subscriptions WHERE user_id = {user_id}")
        result = self.cursor.fetchone()
        result = result['password'] if result is not None else False
        return result
        
    @SQLighter.check_connection
    def add_user(self,user_id):
        self.cursor.execute(f"INSERT INTO subscriptions (user_id) VALUES ({user_id})")
        self.commit()

    @SQLighter.check_connection
    def add_username(self,user_id,username):
        self.cursor.execute(f"UPDATE subscriptions SET username = '{username}' WHERE user_id = {user_id}")


    @SQLighter.check_connection
    def add_password(self,user_id,password):
        self.cursor.execute(f"UPDATE subscriptions SET password = {password} WHERE user_id = {user_id}")

    @SQLighter.check_connection
    def add_account(self,user_id):
        self.cursor.execute(f"UPDATE subscriptions SET hasAccount = {True} WHERE user_id = {user_id}")
        self.commit()

    @SQLighter.check_connection
    def delete_user(self,user_id):
        self.cursor.execute(f"DELETE FROM subscriptions WHERE user_id = {user_id}")


def main():
    pass

if __name__ == '__main__':
    main()
