import json
import logging

from chatbox.app.constants import chat_internal_codes as _c

from chatbox.app.core.components.client.commands import Command
from chatbox.app.core.components.client.controller.base import BaseControllerClient


_logger = logging.getLogger(__name__)


class ControllerMessageClient(BaseControllerClient):

	def list_user(self, action: Command) -> None:
		code = _c.Codes[action.name]
		command = _c.make_message(code, code.name)
		self.chat.send_to_server(command)

	def list_group_or_channel(self, action: Command, user_input: str) -> None:
		name = self.get_command_args(user_input)
		code = _c.Codes[action.name]

		payload = {"name": name.strip()}
		command = _c.make_message(code, json.dumps(payload))
		self.chat.send_to_server(command)

	def delete(self, user_input: str) -> None:
		message_id = self.get_command_args(user_input)

		payload = {"message_id": message_id.strip()}
		command = _c.make_message(_c.Codes.MESSAGE_DELETE, json.dumps(payload))
		self.chat.send_to_server(command)
