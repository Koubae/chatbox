import logging
import typing as t
from abc import abstractmethod

from chatbox.app.database.orm.abstract_connector import Connector
from chatbox.app.database.orm.sqlite_conn import SQLITEConnection, SQLITEConnectionException
from chatbox.app.database.orm.types import Item, T


_logger = logging.getLogger(__name__)
QUERY_REPLACE_KEYS: t.Final[frozenset] = frozenset({
	"__table",
	"__name",
	"__columns",
	"__params",
})
QUERY_REPLACE_KEY_EQUAL: t.Final[str] = "__placeholder = __value"


class RepositoryBase(Connector):
	_get_query = "SELECT * FROM __table WHERE id = :id"
	_get_query_by_name = "SELECT * FROM __table WHERE __name = :__name"
	_get_many_query = "SELECT * FROM __table LIMIT :limit OFFSET :offset"
	_create_query = "INSERT INTO __table (__columns) VALUES (__params)"
	_update_query = f"UPDATE __table SET {QUERY_REPLACE_KEY_EQUAL} WHERE id = :id"
	_delete_query = f"DELETE FROM __table WHERE id = :id"

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
	def _columns(self) -> str: ...

	@abstractmethod
	def _build_object(self, data: Item) -> t.Any: ...

	def get(self, _id: int) -> T | None:
		try:
			return self._build_object(self.db.get(self.__query_build(self._get_query), {"id": _id}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while get {self._table} {_id}, reason {error}")
			return None

	def get_by_name(self, name: int | str) -> T | None:
		try:
			return self._build_object(self.db.get(self.__query_build(self._get_query_by_name), {self._name: name}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while get {self._table} by name {name}, reason {error}")
			return None

	def get_many(self, limit: int = 100, offset: int = 0) -> list[T]:
		try:
			return self._build_objects(self.db.get_many(self.__query_build(self._get_many_query), {"limit": limit, "offset": offset}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while get-many {self._table}, limit = {limit}, offset = {offset}, reason {error}")
			return []

	def create(self, data: t.Iterable[dict] | dict) -> T | None:
		if isinstance(data, dict):
			data = (data, )

		try:
			self.db.create(self.__query_build(self._create_query), data)
		except SQLITEConnectionException as error:
			_logger.error(f"Error while creating new {self._table}, reason {error}")
			return None
		else:
			self.created = self.db.created
			created_id: int | None = self.db.cursor.lastrowid
			if not created_id:
				return None
			return self.get(created_id)

	def update(self, _id: int, data: dict) -> T | None:
		data["id"] = _id

		try:
			self.db.update(self.__query_build(self._update_query, data), data)
		except SQLITEConnectionException as error:
			_logger.error(f"Error while updating new {self._table} for item id {_id}, reason {error}")
			return None
		else:
			self.updated = self.db.updated
			return self.get(_id)

	def delete(self, _id: int) -> bool:
		try:
			self.db.delete(self.__query_build(self._delete_query), {"id": _id})
		except SQLITEConnectionException as error:
			_logger.error(f"Error while deleting {self._table} item id {_id}, reason {error}")
			return False
		else:
			self.deleted = self.db.deleted
			return True

	def _build_objects(self, data: t.Iterable[Item]) -> list:
		return [item for item in [self._build_object(item_raw) for item_raw in data]]

	def __query_build(self, query: str, params: t.Optional[dict] = None) -> str:
		if QUERY_REPLACE_KEY_EQUAL in query:
			if not params:
				raise RuntimeError(f"Query {query} contains keys {QUERY_REPLACE_KEY_EQUAL} but no params was provided!")
			set_query = [f"{key} = :{key}" for key, value in params.items()]
			query = query.replace("__placeholder = __value", ", ".join(set_query))

		for key in sorted(list(QUERY_REPLACE_KEYS)):
			if key == "__params":
				value = getattr(self, "_columns")
				value_params = ", ".join([f":{v}" for v in value])
				query = query.replace(key, value_params)
				continue

			value = getattr(self, key[1:])
			if key == "__columns":
				value = ", ".join(value)
			query = query.replace(key, value)

		_logger.info("Build Query : %s", query)
		return query
