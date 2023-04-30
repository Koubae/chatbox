import typing as t
from abc import abstractmethod

from chatbox.app.database.orm.abstract_connector import Connector
from chatbox.app.database.orm.sqlite_conn import SQLITEConnection
from chatbox.app.database.orm.types import SQLParams, Item


class RepositoryBase(Connector):
	def __init__(self, database: SQLITEConnection):
		super().__init__()
		self._database: SQLITEConnection = database

	def get(self, query: str, parameters: SQLParams = None) -> Item | None:
		return self._database.get(query, parameters)

	def list(self, query: str, parameters: SQLParams = None) -> list[Item]:
		return self._database.list(query, parameters)

	def create(self, query: str, parameters: t.Iterable[SQLParams] = None) -> t.Self:
		self._database.create(query, parameters)
		self.created = self._database.created
		return self

	def update(self, query: str, parameters: SQLParams = None) -> t.Self:
		self._database.update(query, parameters)
		self.updated = self._database.updated
		return self

	def delete(self, query: str, parameters: SQLParams = None) -> t.Self:
		self._database.delete(query, parameters)
		self.deleted = self._database.deleted
		return self

	@property
	@abstractmethod
	def _table_name(self) -> str: ...

	@abstractmethod
	def _build_object(self, data: Item) -> t.Any: ...

	def _build_objects(self, data: t.Iterable[Item]) -> list:
		return [item for item in [self._build_object(item_raw) for item_raw in data]]