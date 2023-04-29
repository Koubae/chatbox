from types import MappingProxyType

# TODO: make enums!
LOGIN = 1
IDENTIFICATION = 2
IDENTIFICATION_REQUIRED = 3
LOGIN_SUCCESS = 4

CODES: MappingProxyType[int, str] = MappingProxyType({
	LOGIN: 'LOGIN',
	IDENTIFICATION: 'IDENTIFICATION',
	IDENTIFICATION_REQUIRED: 'IDENTIFICATION_REQUIRED',
	LOGIN_SUCCESS: 'LOGIN_SUCCESS',
})

CODE_IDENTIFIER_LEFT: str = "@@##"
CODE_IDENTIFIER_RIGHT: str = " --"


class ChatInternalCodeException(Exception):
	pass


full_code = lambda _code: f"{CODE_IDENTIFIER_LEFT}{_code}{CODE_IDENTIFIER_RIGHT}"


def code_in(code: int, message: str) -> int:
	_code = CODES.get(code, None)
	if not _code:
		return 0
	if f"{full_code(_code)}" in message:
		return code
	return 0


def get_message(code: int, message: str) -> str | None:
	_code = CODES.get(code, None)
	if not _code:
		return None
	return message.replace(full_code(_code), "")


def make_message(code: int, message: str) -> str:
	_code = CODES.get(code, None)
	if not _code:
		ChatInternalCodeException(f"code {_code} not mapped in CODES")
	code_build = full_code(_code)
	return f"{code_build}{message}"
