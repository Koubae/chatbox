import typing as t


SQLParams = t.Mapping[str, str | bytes | bytearray | memoryview | list | int | float | None]
Item = dict[str | int, t.Any]
T = t.TypeVar('T')