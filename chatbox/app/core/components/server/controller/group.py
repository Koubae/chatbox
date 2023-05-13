import logging
import json

from chatbox.app.core.components.commons.controller.base import BaseController
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.model.group import GroupModel
from chatbox.app.core.model.message import ServerMessageModel
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class ControllerGroup(BaseController):

	def list_(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.GROUP_LIST, payload)  # noqa

		groups: list[GroupModel] = self.chat.repo_group.list_user_group(client_conn.user.id)

		group_names = [group.to_json() for group in groups]
		self.chat.send_to_client(client_conn, _c.make_message(_c.Codes.GROUP_LIST, json.dumps(group_names)))

	def create(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.GROUP_CREATE, payload)  # noqa

		group_owner, group_info, group_name = self._get_group_data(payload)
		group_members = self._get_group_members(client_conn, group_info)

		group_exists: GroupModel = self.chat.repo_group.get_by_name(group_name)
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
		_c.remove_chat_code_from_payload(_c.Codes.GROUP_UPDATE, payload)  # noqa

		group_owner, group_info, group_name = self._get_group_data(payload)

		group_exists: GroupModel = self.chat.repo_group.get_by_name(group_name)
		if not group_exists:
			self.chat.send_to_client(client_conn, f"Group {group_name} cannot be created, group does not exist.")
			return

		group_members = self._get_group_members(client_conn, group_info)


		group: GroupModel = self.chat.repo_group.update(group_exists.id,
														{"name": group_name, "owner_id": group_owner, "members": json.dumps(group_members)})
		if not group:
			self.chat.send_to_client(client_conn, f"Error while updating group {group_name}!")
			return

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} updated group --> {group}")
		self.chat.send_to_client(client_conn, f"Group {group_name} updated successfully")

	def delete(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.GROUP_DELETE, payload)  # noqa

		group_owner, group_info, group_name = self._get_group_data(payload)

		group_exists: GroupModel = self.chat.repo_group.get_by_name(group_name)
		if not group_exists:
			self.chat.send_to_client(client_conn, f"Group {group_name} cannot be deleted, group does not exist.")
			return

		if group_exists.owner_id != group_owner:
			self.chat.send_to_client(client_conn, f"You are not owner of Group {group_name}!")
			return

		deleted = self.chat.repo_group.delete(group_exists.id)
		if not deleted:
			_logger.info(f"user {client_conn.user.username} {client_conn.user.id} "
						 f"try to delete  group {group_exists.name} {group_exists.id} but something went wrong")
			self.chat.send_to_client(client_conn, f"Group {group_exists.name} {group_exists.id} could not be deleted")
		else:
			_logger.info(f"user {client_conn.user.username} {client_conn.user.id} delete  group {group_exists.name} {group_exists.id}")
			self.chat.send_to_client(client_conn, f"Group {group_exists.name} {group_exists.id} deleted successfully")

	def leave(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.GROUP_LEAVE, payload)  # noqa

		group_owner, group_info, group_name = self._get_group_data(payload)

		group_exists: GroupModel = self.chat.repo_group.get_by_name(group_name)
		if not group_exists:
			self.chat.send_to_client(client_conn, f"You cannot a Group {group_name}, group does not exist.")
			return

		if group_exists.owner_id == group_owner:
			self.chat.send_to_client(client_conn, f"You cannot leave this group {group_name} because you are the owner!")
			return

		user_to_remove: str = client_conn.user.username
		if client_conn.user.username not in group_exists.members:
			self.chat.send_to_client(client_conn, f"You are not a member of Group {group_name}!")
			return

		members_current = set(group_exists.members)
		member_to_remove = {user_to_remove}
		members_updated = members_current - member_to_remove

		group: GroupModel = self.chat.repo_group.update(group_exists.id,{"members": json.dumps(list(members_updated))})
		if not group:
			self.chat.send_to_client(client_conn, f"Error while leaving group {group_name}!")
			return

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} successfully left group --> {group}")
		self.chat.send_to_client(client_conn, f"You left Group {group_name}")

	def _get_group_data(self, payload: ServerMessageModel) -> tuple[str | int, dict, str]:
		group_owner = payload.owner.identifier
		group_info: dict = self.json_decode(payload.body)
		group_name: str = group_info["name"]
		return group_owner, group_info, group_name

	@staticmethod
	def _get_group_members(client_conn, group_info: dict) -> list[str]:
		group_members: list = [member.strip() for member in group_info["members"]]
		group_members.insert(0, client_conn.user.username)
		return group_members
