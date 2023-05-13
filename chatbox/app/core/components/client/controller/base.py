import logging

from chatbox.app.core import tcp
from chatbox.app.core.components.commons.controller.base import BaseController, BaseControllerException
from chatbox.app.core.components.commons.functions import get_command_target

_logger = logging.getLogger(__name__)


class ControllerClientException(BaseControllerException):
	pass


class BaseControllerClient(BaseController):
	def __init__(self, chat: 'tcp.SocketTCPClient', terminal: 'components.client.ui Terminal'):
		super().__init__(chat)
		self.ui: 'components.client.ui Terminal' = terminal

	@staticmethod
	def get_command_args(user_input: str) -> str:
		command_args = get_command_target(user_input)
		if not command_args:
			raise ControllerClientException(f"Command target missing, command is {user_input}")
		return command_args