import typing as t
from abc import ABC, abstractmethod

from chatbox.app.database.orm.types import Item


class Connector(ABC):
	def __init__(self):
		self.__last_count_created: int = -1
		self.__last_count_updated: int = -1
		self.__last_count_deleted: int = -1

	@property
	def created(self) -> int:
		return self.__last_count_created

	@created.setter
	def created(self, value: int) -> None:
		self.__last_count_created = value

	@property
	def updated(self) -> int:
		return self.__last_count_updated

	@updated.setter
	def updated(self, value: int) -> None:
		self.__last_count_updated = value

	@property
	def deleted(self) -> int:
		return self.__last_count_deleted

	@deleted.setter
	def deleted(self, value: int) -> None:
		self.__last_count_deleted = value

	@abstractmethod
	def get(self, *_, **__) -> Item | None: ...

	@abstractmethod
	def list(self, *_, **__) -> list[Item]: ...

	@abstractmethod
	def create(self, *_, **__) -> t.Self: ...

	@abstractmethod
	def update(self, *_, **__) -> t.Self: ...

	@abstractmethod
	def delete(self, *_, **__) -> t.Self: ...
