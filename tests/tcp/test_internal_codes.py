import pytest

from chatbox.app.constants import chat_internal_codes as _c


class TestChatInternalCodes:

	@pytest.mark.tcp_codes
	@pytest.mark.tcp
	def test_chat_code_contains_identifiers(self):
		code = _c.full_code(_c.Codes.IDENTIFICATION)

		assert _c.Codes.IDENTIFICATION.name in code and _c.CODE_IDENTIFIER_LEFT in code and _c.CODE_IDENTIFIER_RIGHT in code

	@pytest.mark.tcp_codes
	@pytest.mark.tcp
	def test_code_scan_finds_code(self):
		my_message = f"{_c.full_code(_c.Codes.IDENTIFICATION.name)} - my message"

		code_scanned = _c.code_scan(my_message)

		assert code_scanned is _c.Codes.IDENTIFICATION


	@pytest.mark.tcp_codes
	@pytest.mark.tcp
	def test_code_scan_returns_none_when_code_is_not_found(self):
		my_message = f"{_c.full_code('CODE_NOT_EXISTS__')} - my message"

		code_scanned = _c.code_scan(my_message)

		assert code_scanned is None
		