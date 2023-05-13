import json
import logging
import typing as t
from chatbox.app.core import tcp


_logger = logging.getLogger(__name__)


class BaseControllerException(Exception):
	pass


class BaseController:
	def __init__(self, chat: t.Union['tcp.SocketTCPServer',  'tcp.SocketTCPClient']):
		self.chat: t.Union['tcp.SocketTCPServer',  'tcp.SocketTCPClient'] = chat

	@staticmethod
	def json_decode(payload: str) -> dict | list:
		try:
			return json.loads(payload)
		except (json.JSONDecodeError, ValueError, TypeError) as error:
			error_message = f"Error in json_decode, reason : {error}"
			_logger.warning(error_message)
			raise BaseControllerException(f"Error {error_message}")
