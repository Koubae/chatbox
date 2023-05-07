import typing as t
from enum import Enum, auto
from types import MappingProxyType

from chatbox.app.constants.chat_internal_codes import Codes


COMMAND_PREFIX: t.Final[str] = "/"


class Command(Enum):
	QUIT = auto()
	LOGIN = auto()
	LOGOUT = auto()

	SEND_TO_ALL = auto()
	SEND_TO_CHANNEL = auto()
	SEND_TO_GROUP = auto()
	SEND_TO_USER = auto()

	USER_LIST_ALL = auto()
	USER_LIST_LOGGED = auto()
	USER_LIST_UN_LOGGED = auto()

	GROUP_LIST = auto()
	GROUP_CREATE = auto()
	GROUP_UPDATE = auto()
	GROUP_LEAVE = auto()
	GROUP_DELETE = auto()

	CHANNEL_LIST_ALL = auto()
	CHANNEL_LIST_JOINED = auto()
	CHANNEL_LIST_UN_JOINED = auto()
	CHANNEL_CREATE = auto()
	CHANNEL_UPDATE = auto()
	CHANNEL_LEAVE = auto()
	CHANNEL_ADD = auto()
	CHANNEL_JOIN = auto()
	CHANNEL_DELETE = auto()

	def __str__(self):
		return f"{COMMAND_PREFIX}{self.name.lower()}"

class Commands:
	DEFAULT_COMMAND: Command = Command.SEND_TO_ALL
	_command_code_mapping: t.Final[MappingProxyType[Command, Codes]] = MappingProxyType({
		Command.QUIT: Codes.QUIT,
		Command.LOGIN: Codes.LOGIN,
		Command.LOGOUT: Codes.LOGOUT,

		Command.SEND_TO_ALL: Codes.SEND_TO_ALL,
		Command.SEND_TO_CHANNEL: Codes.SEND_TO_CHANNEL,
		Command.SEND_TO_GROUP: Codes.SEND_TO_GROUP,
		Command.SEND_TO_USER: Codes.SEND_TO_USER,

		Command.USER_LIST_ALL: Codes.USER_LIST_ALL,
		Command.USER_LIST_LOGGED: Codes.USER_LIST_LOGGED,
		Command.USER_LIST_UN_LOGGED: Codes.USER_LIST_UN_LOGGED,

		Command.GROUP_LIST: Codes.GROUP_LIST,
		Command.GROUP_CREATE: Codes.GROUP_CREATE,
		Command.GROUP_UPDATE: Codes.GROUP_UPDATE,
		Command.GROUP_LEAVE: Codes.GROUP_LEAVE,
		Command.GROUP_DELETE: Codes.GROUP_DELETE,

		Command.CHANNEL_LIST_ALL: Codes.CHANNEL_LIST_ALL,
		Command.CHANNEL_LIST_JOINED: Codes.CHANNEL_LIST_JOINED,
		Command.CHANNEL_LIST_UN_JOINED: Codes.CHANNEL_LIST_UN_JOINED,
		Command.CHANNEL_CREATE: Codes.CHANNEL_CREATE,
		Command.CHANNEL_UPDATE: Codes.CHANNEL_UPDATE,
		Command.CHANNEL_LEAVE: Codes.CHANNEL_LEAVE,
		Command.CHANNEL_ADD: Codes.CHANNEL_ADD,
		Command.CHANNEL_JOIN: Codes.CHANNEL_JOIN,
		Command.CHANNEL_DELETE: Codes.CHANNEL_DELETE,

	})

	@classmethod
	def read_command(cls, message: str) -> Command:
		user_command = message.strip().lower().split(" ")[0]
		try:
			return next(command for command in Command if str(command) in user_command)
		except StopIteration:
			return cls.DEFAULT_COMMAND
