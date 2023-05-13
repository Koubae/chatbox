import logging
import typing as t

from chatbox.app.core.components.client.controller.base import BaseControllerClient
from chatbox.app.core.model.message import ServerMessageModel
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class ControllerSendToClient(BaseControllerClient):

	def user(self, user_input: str) -> None:
		user = self.get_command_args(user_input)

		user_input = self.ui.message_prompt(f"@{user} : ")
		self.chat.send_to_user(user, user_input)

	def group(self, client_conn: objects.Client, payload: ServerMessageModel) -> None: ...

	def channel(self, client_conn: objects.Client, payload: ServerMessageModel) -> None: ...

	def all(self, user_input: t.Optional[str] = None) -> None:
		if user_input is None:
			user_input = self.ui.message_prompt(f"@[ALL] : ")
		self.chat.send_to_all(user_input)
