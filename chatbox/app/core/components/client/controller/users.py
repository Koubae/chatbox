
from chatbox.app.constants import chat_internal_codes as _c
import logging

from chatbox.app.core.components.client.commands import Command
from chatbox.app.core.components.client.controller.base import BaseControllerClient


_logger = logging.getLogger(__name__)


class ControllerUsersClient(BaseControllerClient):

	def list_(self, action: Command) -> None:
		code = _c.Codes[action.name]
		command = _c.make_message(code, code.name)
		self.chat.send_to_server(command)
