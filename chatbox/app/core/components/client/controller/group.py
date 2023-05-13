import json

from chatbox.app.constants import chat_internal_codes as _c
import logging

from chatbox.app.core.components.client.controller.base import BaseControllerClient, ControllerClientException


_logger = logging.getLogger(__name__)


class ControllerGroupClient(BaseControllerClient):

	def list_(self) -> None:
		group_command = _c.make_message(_c.Codes.GROUP_LIST, _c.Codes.GROUP_LIST.name)
		self.chat.send_to_server(group_command)

	def create(self, user_input: str) -> None:
		return self._create_update(user_input, _c.Codes.GROUP_CREATE)

	def update(self, user_input: str) -> None:
		return self._create_update(user_input, _c.Codes.GROUP_UPDATE)

	def delete(self, user_input: str) -> None:
		group_name, _ = self._get_group_info(user_input)

		payload = {"name": group_name.strip()}
		group_command = _c.make_message(_c.Codes.GROUP_DELETE, json.dumps(payload))
		self.chat.send_to_server(group_command)

	def leave(self, user_input: str) -> None:
		group_name, _ = self._get_group_info(user_input)

		payload = {"name": group_name.strip()}
		group_command = _c.make_message(_c.Codes.GROUP_LEAVE, json.dumps(payload))
		self.chat.send_to_server(group_command)

	def _create_update(self, user_input: str, code: _c.Codes) -> None:
		group_name, group_members = self._get_group_info(user_input)

		group_members = list(set(group_members) - {self.chat.user_name})
		if not group_members:
			raise ControllerClientException("Groups members required!")
		group_members = [group.strip() for group in group_members]

		payload = {"name": group_name, "members": group_members}
		group_command = _c.make_message(code, json.dumps(payload))
		self.chat.send_to_server(group_command)

	def _get_group_info(self, user_input: str) -> tuple[str, list[str]]:
		group_info = self.get_command_args(user_input)
		group_name, *group_members = group_info.split(" ")
		return group_name, group_members