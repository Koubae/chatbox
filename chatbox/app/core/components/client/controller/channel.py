import json

from chatbox.app.constants import chat_internal_codes as _c
import logging

from chatbox.app.core.components.client.commands import Command
from chatbox.app.core.components.client.controller.base import BaseControllerClient, ControllerClientException


_logger = logging.getLogger(__name__)


class ControllerChannelClient(BaseControllerClient):

	def list_all(self) -> None:
		command = _c.make_message(_c.Codes.CHANNEL_LIST_ALL, _c.Codes.CHANNEL_LIST_ALL.name)
		self.chat.send_to_server(command)

	def list_owned(self) -> None:
		command = _c.make_message(_c.Codes.CHANNEL_LIST_OWNED, _c.Codes.CHANNEL_LIST_OWNED.name)
		self.chat.send_to_server(command)

	def create(self, user_input: str) -> None:
		return self._create_update(user_input, _c.Codes.CHANNEL_CREATE)

	def update(self, user_input: str) -> None:
		return self._create_update(user_input, _c.Codes.CHANNEL_UPDATE)

	def delete(self, user_input: str) -> None:
		name, _ = self._get_channel_info(user_input)

		payload = {"name": name.strip()}
		command = _c.make_message(_c.Codes.CHANNEL_DELETE, json.dumps(payload))
		self.chat.send_to_server(command)

	# ---------------------
	# Channel Member Management
	# ---------------------

	def join(self, user_input: str) -> None:
		name, _ = self._get_channel_info(user_input)

		payload = {"name": name.strip()}
		command = _c.make_message(_c.Codes.CHANNEL_JOIN, json.dumps(payload))
		self.chat.send_to_server(command)

	def member_action(self, user_input: str, action: Command) -> None:
		name, _ = self._get_channel_info(user_input)

		payload = {"name": name.strip()}
		code = _c.Codes[action.name]
		command = _c.make_message(code, json.dumps(payload))
		self.chat.send_to_server(command)

	def _create_update(self, user_input: str, code: _c.Codes) -> None:
		name, members = self._get_channel_info(user_input)

		members = list(set(members) - {self.chat.user_name})
		if not members:
			raise ControllerClientException("Channel members required!")
		members = [member.strip() for member in members]

		payload = {"name": name, "members": members}
		command = _c.make_message(code, json.dumps(payload))
		self.chat.send_to_server(command)

	def _get_channel_info(self, user_input: str) -> tuple[str, list[str]]:
		info = self.get_command_args(user_input)
		name, *members = info.split(" ")
		return name, members