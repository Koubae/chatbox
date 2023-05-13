import json

from chatbox.app.constants import chat_internal_codes as _c
import logging

from chatbox.app.core.components.client.controller.base import BaseControllerClient, ControllerClientException
from chatbox.app.core.components.commons.functions import get_command_target


_logger = logging.getLogger(__name__)


class ControllerGroupClient(BaseControllerClient):

	def list(self) -> None:
		group_command = _c.make_message(_c.Codes.GROUP_LIST, _c.Codes.GROUP_CREATE.name)
		self.chat.send_to_server(group_command)

	def create(self, user_input: str) -> None:
		return self._create_update(user_input, _c.Codes.GROUP_CREATE)

	def update(self, user_input: str) -> None:
		return self._create_update(user_input, _c.Codes.GROUP_UPDATE)

	def _create_update(self, user_input: str, code: _c.Codes) -> None:
		group_info = get_command_target(user_input)
		if not group_info:
			raise ControllerClientException("Command target missing")

		group_name, *group_members = group_info.split(" ")
		group_members = list(set(group_members) - {self.chat.user_name})
		if not group_members:
			raise ControllerClientException("Groups members required!")
		group_members = [group.strip() for group in group_members]

		payload = {"name": group_name, "members": group_members}
		group_command = _c.make_message(code, json.dumps(payload))
		self.chat.send_to_server(group_command)
