import typing as t
from enum import Enum, auto

SQLParams = t.Mapping[str, str | bytes | bytearray | memoryview | list | int | float | None]
Item = dict[str | int, t.Any]
T = t.TypeVar('T')


class DatabaseOperations(Enum):
	READ = auto()
	READ_MANY = auto()

	WRITE_CREATE = auto()
	WRITE_CREATE_MANY = auto()
	WRITE_UPDATE = auto()

	DELETE = auto()
	DELETE_MANY = auto()
