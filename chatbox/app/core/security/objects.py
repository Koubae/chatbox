from enum import Enum


class Access(Enum):
	GRANTED = True
	DENIED = False
	CREATED = -1
