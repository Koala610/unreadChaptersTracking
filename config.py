import sqlite3
connection = sqlite3.connect('1.db')
cursor = connection.cursor()



API_TOKEN = cursor.execute("SELECT token FROM settings WHERE id = 0").fetchall()[0][0]