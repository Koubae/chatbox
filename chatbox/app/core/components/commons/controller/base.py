import typing as t
from chatbox.app.core import tcp
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.model.message import ServerMessageModel


class BaseController:
	def __init__(self, chat: t.Union['tcp.SocketTCPServer',  'tcp.SocketTCPClient']):
		self.chat: t.Union['tcp.SocketTCPServer',  'tcp.SocketTCPClient'] = chat

	@staticmethod
	def _remove_chat_code_from_payload(code: _c.Codes, payload: ServerMessageModel) -> None:
		body = _c.get_message(code, payload.body)
		if not body:
			return

		payload.body = body
