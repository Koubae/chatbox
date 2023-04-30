import os
import sqlite3
import logging
import typing as t
from enum import Enum

from chatbox.app.database.orm.abstract_connector import Connector
from chatbox.app.database.orm.types import SQLParams, Item


_logger = logging.getLogger(__name__)


class SQLExecution(Enum):
	EXECUTE_ONE = 1
	EXECUTE_MANY = 2
	EXECUTE_SCRIPT = 3


class SQLCRUDOperation(Enum):
	READ = 1
	LIST = 2
	CREATE = 3
	UPDATE = 4
	DELETE = 5


class SQLITEConnectionException(Exception):
	ERROR_RUNTIME: t.Final[str] = "[DB_ERROR_RUNTIME] - Something when wrong"
	ERROR_SCHEMA_INIT_NOT_FOUND: t.Final[str] = "[DB_ERROR_SCHEMA_INIT_NOT_FOUND] - Schema %s not found"
	ERROR_GET: t.Final[str] = "[DB_ERROR_GET] - Error while get resource"
	ERROR_LIST: t.Final[str] = "[DB_ERROR_GET] - Error while list resource"
	ERROR_CREATE: t.Final[str] = "[DB_ERROR_CREATE] - Error while create resource"
	ERROR_UPDATE: t.Final[str] = "[DB_ERROR_CREATE] - Error while update resource"
	ERROR_DELETE: t.Final[str] = "[DB_ERROR_DELETE] - Error while delete resource"

	@staticmethod
	def error_type(_type: SQLCRUDOperation) -> str:
		match _type:
			case SQLCRUDOperation.READ:
				return SQLITEConnectionException.ERROR_GET
			case SQLCRUDOperation.LIST:
				return SQLITEConnectionException.ERROR_LIST
			case SQLCRUDOperation.CREATE:
				return SQLITEConnectionException.ERROR_CREATE
			case SQLCRUDOperation.UPDATE:
				return SQLITEConnectionException.ERROR_UPDATE
			case SQLCRUDOperation.DELETE:
				return SQLITEConnectionException.ERROR_DELETE
			case _:
				raise TypeError(f"Value {_type} is not a valid sql Operation!")


class SQLITEConnection(Connector):

	def __init__(self, database: str, schema: t.Optional[str | os.PathLike] = None):
		super().__init__()
		self.database: str = database

		sqlite3.enable_callback_tracebacks(True)
		sqlite3.threadsafety = 3
		self.connection: sqlite3.Connection = sqlite3.connect(database)
		self.connection.row_factory = sqlite3.Row
		self.cursor: sqlite3.Cursor = self.connection.cursor()

		self.schema: t.Final[str | os.PathLike] = schema
		if self.schema:
			self._init_schema()

	def __del__(self):   # pragma: no cover
		self.connection.close()

	def __call__(self,
		query: str,
		parameters: SQLParams | t.Iterable[SQLParams] = None,
		execution_type: SQLExecution = SQLExecution.EXECUTE_ONE
	) -> t.Self:

		match execution_type:
			case SQLExecution.EXECUTE_ONE:
				self.cursor.execute(query, parameters or {})
			case SQLExecution.EXECUTE_MANY:
				self.cursor.executemany(query, parameters or [{}, ])
			case SQLExecution.EXECUTE_SCRIPT:
				self.cursor.executescript(query)
			case _:
				raise SQLITEConnectionException(f"{SQLITEConnectionException.ERROR_RUNTIME} - execution {execution_type} is not supported.")
		return self

	def get(self, query: str, parameters: SQLParams = None) -> Item | None:
		self._run_query(query, parameters, crud_operation=SQLCRUDOperation.READ)
		item = self.cursor.fetchone()
		return item and dict(item) or None

	def list(self, query: str, parameters: SQLParams = None) -> list[Item]:
		self._run_query(query, parameters, crud_operation=SQLCRUDOperation.LIST)
		return [dict(item) for item in self.cursor.fetchall()]

	def create(self, query: str, parameters: t.Iterable[SQLParams] = None) -> t.Self:
		self._run_query(query, parameters, crud_operation=SQLCRUDOperation.CREATE, execution_type=SQLExecution.EXECUTE_MANY)
		self.created = self.cursor.rowcount
		return self

	def update(self, query: str, parameters: SQLParams = None) -> t.Self:
		def _inject_modified_timestamp():
			query_block = query.split("SET")
			query_block.insert(1, "SET modified = CURRENT_TIMESTAMP, ")
			return " ".join(query_block)
		query = _inject_modified_timestamp()

		self._run_query(query, parameters, crud_operation=SQLCRUDOperation.UPDATE)
		self.updated = self.cursor.rowcount
		return self

	def delete(self, query: str, parameters: SQLParams = None) -> t.Self:
		self._run_query(query, parameters, crud_operation=SQLCRUDOperation.DELETE)
		self.deleted = self.cursor.rowcount
		return self

	def _run_query(self,
		query: str,
		parameters: SQLParams | t.Iterable[SQLParams],
		crud_operation: SQLCRUDOperation,
		execution_type: SQLExecution = SQLExecution.EXECUTE_ONE
	) -> None:
		try:
			with self.connection:
				self(query, parameters, execution_type)
		except sqlite3.Error as sqlite_error:
			error_type = SQLITEConnectionException.error_type(crud_operation)
			_logger.exception(f"{error_type}, reason: {sqlite_error}", exc_info=sqlite_error)
			raise SQLITEConnectionException(f"{error_type} - {sqlite_error}") from None

	def _init_schema(self):
		try:
			with open(self.schema, "r") as file:
				schema = file.read()
		except FileNotFoundError as error:
			raise SQLITEConnectionException(f"{SQLITEConnectionException.ERROR_SCHEMA_INIT_NOT_FOUND % self.schema}, error: {error}") from None
		else:
			self._run_query(schema, None, crud_operation=SQLCRUDOperation.CREATE, execution_type=SQLExecution.EXECUTE_SCRIPT)
