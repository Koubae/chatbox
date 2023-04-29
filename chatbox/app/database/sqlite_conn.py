import sqlite3
import typing as t


class SQLITEConnection:

	def __init__(self, database: str):
		self.database: str = database

		sqlite3.enable_callback_tracebacks(True)
		sqlite3.threadsafety = 3
		self.connection: sqlite3.Connection = sqlite3.connect(database)
		self.connection.row_factory = sqlite3.Row
		self.cursor: sqlite3.Cursor = self.connection.cursor()

	def __del__(self):
		self.connection.close()

	def __call__(self, query: str, parameters: t.Mapping[str, str | bytes | bytearray | memoryview | list | int | float | None] = None) -> t.Self:
		if not parameters:
			parameters = {}
		self.cursor.execute(query, parameters)

		return self
