import logging
import json

from chatbox.app.core.components.commons.controller.base import BaseController
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.model.group import GroupModel
from chatbox.app.core.model.message import ServerMessageModel
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class ControllerGroup(BaseController):

	def list(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		self._remove_chat_code_from_payload(_c.Codes.GROUP_LIST, payload)  # noqa

		groups: list[GroupModel] = self.chat.repo_group.list_user_group(client_conn.user.id)

		group_names = [group.to_json() for group in groups]
		self.chat.send_to_client(client_conn, _c.make_message(_c.Codes.GROUP_LIST, json.dumps(group_names)))

	def create(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		self._remove_chat_code_from_payload(_c.Codes.GROUP_CREATE, payload)  # noqa

		group_owner = payload.owner.identifier
		group_info: dict = json.loads(payload.body)
		group_name: str = group_info["name"]
		group_members: list = [member.strip() for member in group_info["members"]]
		group_members.insert(0, client_conn.user.username)

		group_exists = self.chat.repo_group.get_by_name(group_name)
		if group_exists:
			self.chat.send_to_client(client_conn, f"Group {group_name} already exists!")
			return
		group: GroupModel = self.chat.repo_group.create({"name": group_name, "owner_id": group_owner, "members": json.dumps(group_members)})
		if not group:
			self.chat.send_to_client(client_conn, f"Error while creating group {group_name}!")
			return

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} created new group --> {group}")
		self.chat.send_to_client(client_conn, f"Group {group_name} created successfully")

	def update(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		self._remove_chat_code_from_payload(_c.Codes.GROUP_UPDATE, payload)  # noqa

		group_owner = payload.owner.identifier
		group_info: dict = json.loads(payload.body)
		group_name: str = group_info["name"]

		group_exists = self.chat.repo_group.get_by_name(group_name)
		if not group_exists:
			self.chat.send_to_client(client_conn, f"Group {group_name} cannot be created, group does not exist.")
			return

		group_members: list = [member.strip() for member in group_info["members"]]
		group_members.insert(0, client_conn.user.username)


		group: GroupModel = self.chat.repo_group.update(group_exists.id,
														{"name": group_name, "owner_id": group_owner, "members": json.dumps(group_members)})
		if not group:
			self.chat.send_to_client(client_conn, f"Error while updating group {group_name}!")
			return

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} created new group --> {group}")
		self.chat.send_to_client(client_conn, f"Group {group_name} updated successfully")
