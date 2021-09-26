import sqlite3

class SQLighter:
    def __init__(self,database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status = True):
        with self.connection:
            return self.cursor.execute(f"SELECT id FROM subscriptions WHERE status = ?",(status,)).fetchall()

    def user_exists(self,user_id):
        result = self.cursor.execute(f"SELECT * FROM subscriptions WHERE user_id = ? ",(user_id,)).fetchall()
        return bool(len(result))

    def account_exists(self,user_id):
        result = self.cursor.execute(f"SELECT hasAccount FROM subscriptions WHERE user_id = ? ",(user_id,)).fetchall()
        try:
            return bool(result[0][0])
        except IndexError:
            return False

    def add_user(self,user_id):
        with self.connection:
            return self.cursor.execute(f"INSERT INTO subscriptions (user_id) VALUES (?)",(user_id,))
        self.commit()

    def add_username(self,user_id,username):
        self.cursor.execute(f"UPDATE subscriptions SET username = ? WHERE user_id = ?",(username,user_id))

    def add_password(self,user_id,password):
        self.cursor.execute(f"UPDATE subscriptions SET password = ? WHERE user_id = ?",(password,user_id))

    def add_account(self,user_id):
        self.cursor.execute(f"UPDATE subscriptions SET hasAccount = ? WHERE user_id = ?",(True,user_id))
        self.commit()

    def update_subscription(self,user_id,status):
        #return self.cursor.execute("UPDATE 'subscriptions' SET 'status' = ?",(status,))
        self.cursor.execute(f"UPDATE subscriptions SET status = ? WHERE user_id = ?",(status,user_id))
        self.commit()

    def delete_user(self,user_id):
        return self.cursor.execute(f"DELETE FROM subscriptions WHERE user_id = ?",(user_id,))

    def close(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()


def main():
    user_id = '335271283'
    db = SQLighter('1.db')
    db.add_username(user_id, "123")
    #print(db.get_subscriptions()[0][0])
    #print(db.account_exists(user_id))
    #db.update_subscription(user_id,False)
    #db.delete_user(user_id)
    db.close()

if __name__ == '__main__':
    main()
