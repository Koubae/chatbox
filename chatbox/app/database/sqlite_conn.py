import sqlite3
import logging
import typing as t

from chatbox.app.database.types import SQLParams

_logger = logging.getLogger(__name__)


class SQLITEConnectionException(Exception):
	ERROR_GET: t.Final[str] = "[DB_ERROR_GET] - Error while get resource"
	ERROR_LIST: t.Final[str] = "[DB_ERROR_GET] - Error while list resource"
	ERROR_CREATE: t.Final[str] = "[DB_ERROR_CREATE] - Error while create resource"
	ERROR_UPDATE: t.Final[str] = "[DB_ERROR_CREATE] - Error while update resource"
	ERROR_DELETE: t.Final[str] = "[DB_ERROR_DELETE] - Error while delete resource"


class SQLITEConnection:

	def __init__(self, database: str):
		self.database: str = database

		sqlite3.enable_callback_tracebacks(True)
		sqlite3.threadsafety = 3
		self.connection: sqlite3.Connection = sqlite3.connect(database)
		self.connection.row_factory = sqlite3.Row
		self.cursor: sqlite3.Cursor = self.connection.cursor()

		self.__last_count_created = -1
		self.__last_count_updated = -1
		self.__last_count_deleted = -1

	def __del__(self):
		self.connection.close()

	def __call__(self, query: str, parameters: SQLParams = None) -> t.Self:
		self.cursor.execute(query, parameters or {})
		return self

	@property
	def created(self) -> int:
		return self.__last_count_created

	@property
	def updated(self) -> int:
		return self.__last_count_updated

	@property
	def deleted(self) -> int:
		return self.__last_count_deleted

	def get(self, query: str, parameters: SQLParams = None) -> dict | None:
		try:
			self(query, parameters)
		except sqlite3.Error as sqlite_error:
			_logger.exception(f"{SQLITEConnectionException.ERROR_GET}, reason: {sqlite_error}", exc_info=sqlite_error)
			raise SQLITEConnectionException(f"{SQLITEConnectionException.ERROR_GET} - {sqlite_error}") from None
		else:
			item = self.cursor.fetchone()
			return item and dict(item) or None

	def list(self, query: str, parameters: SQLParams = None) -> list[dict[str | int, t.Any]]:
		try:
			self(query, parameters)
		except sqlite3.Error as sqlite_error:
			_logger.exception(f"{SQLITEConnectionException.ERROR_LIST}, reason: {sqlite_error}", exc_info=sqlite_error)
			raise SQLITEConnectionException(f"{SQLITEConnectionException.ERROR_LIST} - {sqlite_error}") from None
		else:
			return [dict(item) for item in self.cursor.fetchall()]

	def create(self, query: str, parameters: t.Iterable[SQLParams] = None) -> t.Self:
		try:
			with self.connection:
				self.cursor.executemany(query, parameters or {})
		except sqlite3.Error as sqlite_error:
			_logger.exception(f"{SQLITEConnectionException.ERROR_CREATE}, reason: {sqlite_error}", exc_info=sqlite_error)
			raise SQLITEConnectionException(f"{SQLITEConnectionException.ERROR_CREATE} - {sqlite_error}") from None
		else:
			self.__last_count_created = self.cursor.rowcount
			return self

	def update(self, query: str, parameters: t.Iterable[SQLParams] = None) -> t.Self:
		try:
			with self.connection:
				self.cursor.execute(query, parameters or {})
		except sqlite3.Error as sqlite_error:
			_logger.exception(f"{SQLITEConnectionException.ERROR_UPDATE}, reason: {sqlite_error}", exc_info=sqlite_error)
			raise SQLITEConnectionException(f"{SQLITEConnectionException.ERROR_UPDATE} - {sqlite_error}") from None
		else:
			self.__last_count_updated = self.cursor.rowcount
			return self

	def delete(self, query: str, parameters: SQLParams = None) -> t.Self:
		try:
			with self.connection:
				self.cursor.execute(query, parameters or {})
		except sqlite3.Error as sqlite_error:
			_logger.exception(f"{SQLITEConnectionException.ERROR_DELETE}, reason: {sqlite_error}", exc_info=sqlite_error)
			raise SQLITEConnectionException(f"{SQLITEConnectionException.ERROR_DELETE} - {sqlite_error}") from None
		else:
			self.__last_count_deleted = self.cursor.rowcount
			return self
