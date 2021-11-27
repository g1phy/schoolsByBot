import sqlite3


class Database:
	def __init__(self, fileName, debug=False):
		self.connection = sqlite3.connect(fileName, check_same_thread=False)
		if debug:
			self.connection.set_trace_callback(print)

	def getNewCursor(self):
		return self.connection.cursor()

	def commit(self):
		self.connection.commit()

	def create(self):
		self.getNewCursor().execute("CREATE TABLE `users` (`account` integer, `csrf` text, `session` text, `url` text,"
									"`id` integer)")

	def select(self, field, row, value):
		sql = f"SELECT `{field}` FROM `users` WHERE `{row}`=?"
		cursor = self.getNewCursor()
		cursor.execute(sql, [value])
		return cursor.fetchone()

	def insert(self, rows, values):
		sql = f"INSERT INTO `users` ({','.join(rows)}) VALUES ({','.join(values)})"
		cursor = self.getNewCursor()
		cursor.execute(sql)
		self.commit()

	def delete(self, row, value):
		sql = f"DELETE FROM `users` WHERE `{row}`=?"
		cursor = self.getNewCursor()
		cursor.execute(sql, [value])
		self.commit()
