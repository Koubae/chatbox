import json
import logging
import typing as t
from abc import abstractmethod
from datetime import datetime

from chatbox.app.constants import DATETIME_DEFAULT
from chatbox.app.database.orm.abstract_connector import Connector
from chatbox.app.database.orm.sqlite_conn import SQLITEConnection, SQLITEConnectionException
from chatbox.app.database.orm.types import Item, T, DatabaseOperations

_logger = logging.getLogger(__name__)
QUERY_REPLACE_KEYS: t.Final[frozenset] = frozenset({
	"__table",
	"__name",
	"__columns",
	"__params",
})
QUERY_REPLACE_KEY_EQUAL: t.Final[str] = "__placeholder = __value"
QUERY_REPLACE_KEY_NO_EQUAL: t.Final[str] = "__placeholder != __value"
QUERY_REPLACE_KEY_LIKE: t.Final[str] = "__placeholder LIKE __value"


class RepositoryBase(Connector):
	_get_query = "SELECT * FROM `__table` WHERE id = :id"
	_get_query_by_name = "SELECT * FROM `__table` WHERE __name = :__name ORDER BY `created` DESC LIMIT 1"
	_get_many_query = "SELECT * FROM `__table` LIMIT :limit OFFSET :offset"
	_create_query = "INSERT INTO `__table` (__columns) VALUES (__params)"
	_update_query = f"UPDATE `__table` SET {QUERY_REPLACE_KEY_EQUAL} WHERE id = :id"
	_delete_query = "DELETE FROM `__table` WHERE id = :id"

	_operations: tuple[DatabaseOperations] = (
		DatabaseOperations.READ,
		DatabaseOperations.READ_MANY,
		DatabaseOperations.WRITE_CREATE,
		DatabaseOperations.WRITE_CREATE_MANY,
		DatabaseOperations.WRITE_UPDATE,
		DatabaseOperations.DELETE,
		DatabaseOperations.DELETE_MANY,
	)

	def __init__(self, database: SQLITEConnection):
		super().__init__()
		self.__database: SQLITEConnection = database

	@property
	def db(self) -> SQLITEConnection:
		return self.__database

	@property
	@abstractmethod
	def _table(self) -> str: ...

	@property
	@abstractmethod
	def _name(self) -> str: ...

	@property
	@abstractmethod
	def _model(self) -> T: ...

	@property
	def _columns(self):
		return list(self._model.__annotations__.keys())

	def get(self, _id: int) -> T | None:
		if DatabaseOperations.READ not in self._operations:
			raise RuntimeError(f"{self._table} cannot {DatabaseOperations.READ.name}!")

		try:
			return self._build_object(self.db.get(self.__query_build(self._get_query), {"id": _id}))
		except SQLITEConnectionException as error:
			_logger.exception(f"Error while get {self._table} {_id}, reason {error}", exc_info=error)
			return None

	def get_by_name(self, name: int | str) -> T | None:
		if DatabaseOperations.READ not in self._operations:
			raise RuntimeError(f"{self._table} cannot {DatabaseOperations.READ.name}!")

		try:
			return self._build_object(self.db.get(self.__query_build(self._get_query_by_name), {self._name: name}))
		except SQLITEConnectionException as error:
			_logger.exception(f"Error while get {self._table} by name {name}, reason {error}", exc_info=error)
			return None

	def get_many(self, limit: int = 100, offset: int = 0) -> list[T]:
		if DatabaseOperations.READ_MANY not in self._operations:
			raise RuntimeError(f"{self._table} cannot {DatabaseOperations.READ_MANY.name}!")

		try:
			return self._build_objects(self.db.get_many(self.__query_build(self._get_many_query), {"limit": limit, "offset": offset}))
		except SQLITEConnectionException as error:
			_logger.exception(f"Error while get-many {self._table}, limit = {limit}, offset = {offset}, reason {error}", exc_info=error)
			return []

	def create(self, data: t.Iterable[dict] | dict) -> T | None:
		if DatabaseOperations.WRITE_CREATE not in self._operations:
			raise RuntimeError(f"{self._table} cannot {DatabaseOperations.WRITE_CREATE.name}!")

		if isinstance(data, dict):
			data = (data, )

		try:
			self.db.create(self.__query_build(self._create_query), data)
		except SQLITEConnectionException as error:
			_logger.exception(f"Error while creating new {self._table}, data {data}, reason {error}", exc_info=error)
			return None
		else:
			self.created = self.db.created
			created_id: int | None = self.db.cursor.lastrowid
			if not created_id:
				return None
			return self.get(created_id)

	def update(self, _id: int, data: dict) -> T | None:
		if DatabaseOperations.WRITE_UPDATE not in self._operations:
			raise RuntimeError(f"{self._table} cannot {DatabaseOperations.WRITE_UPDATE.name}!")
		query: str = self.__query_build(self._update_query, data)
		data["id"] = _id

		try:
			self.db.update(query, data)
		except SQLITEConnectionException as error:
			_logger.exception(f"Error while updating new {self._table} for item id {_id}, reason {error}", exc_info=error)
			return None
		else:
			self.updated = self.db.updated
			return self.get(_id)

	def delete(self, _id: int) -> bool:
		if DatabaseOperations.DELETE not in self._operations:
			raise RuntimeError(f"{self._table} cannot {DatabaseOperations.DELETE.name}!")

		try:
			self.db.delete(self.__query_build(self._delete_query), {"id": _id})
		except SQLITEConnectionException as error:
			_logger.exception(f"Error while deleting {self._table} item id {_id}, reason {error}", exc_info=error)
			return False
		else:
			self.deleted = self.db.deleted
			return True

	def _build_object(self, data: Item) -> T | None:
		if not data:
			return

		try:
			created = datetime.strptime(data["created"], DATETIME_DEFAULT)
			modified = datetime.strptime(data["modified"], DATETIME_DEFAULT)
		except (KeyError, TypeError, ValueError) as error:
			_logger.exception(f"Error while converting datetime fields of object for table {self._table}, reason {error}", exc_info=error)
			return None

		data["created"] = created
		data["modified"] = modified

		try:
			return self._model(**data)
		except KeyError as error:
			_logger.exception(f"Error while building object for table {self._table}, reason {error}", exc_info=error)

	def _build_objects(self, data: t.Iterable[Item]) -> list:
		return [item for item in [self._build_object(item_raw) for item_raw in data]]

	def _unpack_data(self, _id: str, blob: str) -> dict:
		try:
			return json.loads(blob)
		except (json.JSONDecodeError, TypeError) as error:
			_logger.exception(f"Error while loading session data for {self._table} {_id}, error {error}", exc_info=error)
			return {"error": "__ERROR_LOADING_DATA__"}

	def __query_build(self, query: str, params: t.Optional[dict] = None) -> str:
		query = self.__inject_table_data(query)
		query = self.__inject_parameters(params, query)

		_logger.debug("Build Query : %s", query)
		return query

	def __inject_table_data(self, query):
		for key in sorted(list(QUERY_REPLACE_KEYS)):
			if key == "__params":
				value = getattr(self, "_columns")
				value_params = ", ".join([f":{v}" for v in value])
				query = query.replace(key, value_params)
				continue

			value = getattr(self, key[1:])
			if key == "__columns":
				value = ", ".join([f'`{f}`' for f in value])
			query = query.replace(key, value)
		return query

	@staticmethod
	def __inject_parameters(params, query) -> str:
		if QUERY_REPLACE_KEY_EQUAL in query:
			key_type: str = "="
		elif QUERY_REPLACE_KEY_NO_EQUAL in query:
			key_type: str = "!="
		elif QUERY_REPLACE_KEY_LIKE in query:
			key_type: str = "LIKE"
		else:
			return query
		if not params:
			raise RuntimeError(f"Query {query} contains keys {key_type} but no params was provided!")

		set_query = [f"{key} {key_type} :{key}" for key in params]
		return query.replace("__placeholder = __value", ", ".join(set_query))
