import logging

from chatbox.app.core import tcp
from chatbox.app.core.components.commons.controller.base import BaseController, BaseControllerException


_logger = logging.getLogger(__name__)


class ControllerClientException(BaseControllerException):
	pass


class BaseControllerClient(BaseController):
	def __init__(self, chat: 'tcp.SocketTCPClient', terminal: 'components.client.ui Terminal'):
		super().__init__(chat)
		self.ui: 'components.client.ui Terminal' = terminal
