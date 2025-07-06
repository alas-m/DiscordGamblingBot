import sqlite3

class Database:
	def __init__(self, db_file):
		self.conn = sqlite3.connect(db_file)
		self.cursor = self.conn.cursor()

	def user_exists(self, user_id):
		with self.conn:
			result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchmany(1)
			return bool(len(result))

	def add_user(self, user_id):
		with self.conn:
			return self.cursor.execute("INSERT INTO users (user_id, balance) VALUES (?,?)", (user_id, 10,))

	def mybal(self, user_id):
		with self.conn:
			for i in self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone():
				result = i
			return result

	def update_bal(self, balance, user_id):
		with self.conn:
			return self.cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (balance, user_id,))