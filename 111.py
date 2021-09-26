import sqlite3

connection = sqlite3.connect('1.db')
cursor = connection.cursor()



if input() == 'props':
	print(cursor.execute("SELECT * FROM subscriptions").fetchall())