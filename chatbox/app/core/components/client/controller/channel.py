import json

from chatbox.app.constants import chat_internal_codes as _c
import logging

from chatbox.app.core.components.client.commands import Command
from chatbox.app.core.components.client.controller.base import BaseControllerClient, ControllerClientException


_logger = logging.getLogger(__name__)


class ControllerChannelClient(BaseControllerClient):

	def list_(self, action: Command) -> None:
		code = _c.Codes[action.name]
		command = _c.make_message(code, code.name)
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
	def member_management(self, user_input: str, action: Command) -> None:
		name, members = self._get_channel_info(user_input)

		payload = {"name": name, "members": members}
		code = _c.Codes[action.name]
		command = _c.make_message(code, json.dumps(payload))
		self.chat.send_to_server(command)

	def member_request(self, user_input: str, action: Command) -> None:
		name, _ = self._get_channel_info(user_input)

		payload = {"name": name.strip()}
		code = _c.Codes[action.name]
		command = _c.make_message(code, json.dumps(payload))
		self.chat.send_to_server(command)

	def _create_update(self, user_input: str, code: _c.Codes) -> None:
		name, members = self._get_channel_info(user_input)

		payload = {"name": name, "members": members}
		command = _c.make_message(code, json.dumps(payload))
		self.chat.send_to_server(command)

	def _get_channel_info(self, user_input: str) -> tuple[str, list[str]]:
		info = self.get_command_args(user_input)
		name, *members = info.split(" ")
		return name, self._prepare_members(members)

	def _prepare_members(self, members: list[str]) -> list[str]:
		members = list(set(members) - {self.chat.user_name})
		if not members:
			raise ControllerClientException("Channel members required!")
		members = [member.strip() for member in members]
		return members
