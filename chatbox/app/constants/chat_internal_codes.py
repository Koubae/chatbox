from enum import Enum, auto

from chatbox.app.core.model import message

class Codes(Enum):
	LOGIN = auto()
	IDENTIFICATION = auto()
	IDENTIFICATION_REQUIRED = auto()
	LOGIN_SUCCESS = auto()
	LOGIN_CREATED = auto()

	LOGOUT = auto()
	QUIT = auto()

	SEND_TO_USER = auto()
	SEND_TO_GROUP = auto()
	SEND_TO_CHANNEL = auto()
	SEND_TO_ALL = auto()

	USER_LIST_ALL = auto()
	USER_LIST_LOGGED = auto()
	USER_LIST_UN_LOGGED = auto()

	GROUP_LIST = auto()
	GROUP_CREATE = auto()
	GROUP_UPDATE = auto()
	GROUP_DELETE = auto()
	GROUP_LEAVE = auto()

	CHANNEL_LIST_ALL = auto()
	CHANNEL_LIST_OWNED = auto()
	CHANNEL_LIST_JOINED = auto()
	CHANNEL_LIST_UN_JOINED = auto()
	CHANNEL_CREATE = auto()
	CHANNEL_UPDATE = auto()
	CHANNEL_LEAVE = auto()
	CHANNEL_ADD = auto()
	CHANNEL_REMOVE = auto()
	CHANNEL_JOIN = auto()
	CHANNEL_DELETE = auto()

	MESSAGE_LIST_SENT = auto()
	MESSAGE_LIST_RECEIVED = auto()
	MESSAGE_LIST_GROUP = auto()
	MESSAGE_LIST_CHANNEL = auto()
	MESSAGE_DELETE = auto()

	def __str__(self):
		return f'{self.name}'


CODE_IDENTIFIER_LEFT: str = "@@##"
CODE_IDENTIFIER_RIGHT: str = " --"


class ChatInternalCodeException(Exception):
	pass


full_code = lambda _code: f"{CODE_IDENTIFIER_LEFT}{_code}{CODE_IDENTIFIER_RIGHT}"


def code_in(code: Codes, message: str) -> Codes | None:
	_code = code.name
	max_message_scan = 100
	if not _code:
		return None
	if f"{full_code(_code)}" in message[:max_message_scan]:
		return code
	return None


def code_scan(message: str) -> Codes | None:
	for code in Codes:
		has_code: Codes | None = code_in(code, message)
		if has_code:
			return has_code


def get_message(code: Codes, message: str) -> str | None:
	_code = code.name
	if not _code:
		return None
	return message.replace(full_code(_code), "")


def make_message(code: Codes, message: str) -> str:
	_code = code.name
	code_build = full_code(_code)
	return f"{code_build}{message}"


def remove_chat_code_from_payload(code: Codes, payload: 'message.ServerMessageModel') -> None:
	body = get_message(code, payload.body)
	if not body:
		return

	payload.body = body
