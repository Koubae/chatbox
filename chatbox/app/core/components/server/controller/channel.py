import logging
import json

from chatbox.app.core.components.commons.controller.base import BaseController
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.model.channel import ChannelModel, ChannelMemberModel
from chatbox.app.core.model.message import ServerMessageModel
from chatbox.app.core.model.user import UserModel
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class ControllerChannel(BaseController):

	def list_all(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_LIST_ALL, payload)  # noqa

		# todo
		channels: list[ChannelModel] = self.chat.repo_channel.list_user_channel(client_conn.user.id)

		items = [item.to_json() for item in channels]
		self.chat.send_to_client(client_conn, _c.make_message(_c.Codes.CHANNEL_LIST_ALL, json.dumps(items)))

	def list_owned(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_LIST_OWNED, payload)  # noqa

		channels: list[ChannelModel] = self.chat.repo_channel.list_user_channel(client_conn.user.id)

		items = [item.to_json() for item in channels]
		self.chat.send_to_client(client_conn, _c.make_message(_c.Codes.CHANNEL_LIST_OWNED, json.dumps(items)))

	def create(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_CREATE, payload)  # noqa

		owner, info, name = self._get_data(payload)
		members: list[UserModel] = self._get_members(client_conn, info)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if record:
			self.chat.send_to_client(client_conn, f"Channel {name} already exists!")
			return
		record: ChannelModel = self.chat.repo_channel.create({"name": name, "owner_id": owner})
		if not record:
			self.chat.send_to_client(client_conn, f"Error while creating channel {name}!")
			return

		self.chat.repo_channel_member.create([{"user_id": user.id, "channel_id": record.id}  for user in members])

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} created new channel --> {record} with {len(members)} members!")
		self.chat.send_to_client(client_conn, f"Channel {name} created successfully")

	def update(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_UPDATE, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"Channel {name} cannot be created, channel does not exist.")
			return

		if record.owner_id != owner:
			self.chat.send_to_client(client_conn, f"You are not owner of Channel {name}!")
			return

		members: list[UserModel] = self._get_members(client_conn, info)

		members_update = [member.id for member in members]
		members_current = [member.user_id for member in record.members]
		members_to_delete = set(members_current) - set(members_update)
		members_to_add = set(members_update) - set(members_current)

		for member_delete_id in members_to_delete:  # TODO: implement delete_many!
			self.chat.repo_channel_member.delete(member_delete_id)
		if members_to_add:
			self.chat.repo_channel_member.create([{"user_id": user_id, "channel_id": record.id} for user_id in members_to_add])

		record: ChannelModel = self.chat.repo_channel.update(record.id, {"name": name, "owner_id": owner})
		if not record:
			self.chat.send_to_client(client_conn, f"Error while updating channel {name}!")
			return

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} updated channel --> {record}")
		self.chat.send_to_client(client_conn, f"Channel {name} updated successfully")

	def delete(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_DELETE, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"Channel {name} cannot be deleted, channel does not exist.")
			return

		if record.owner_id != owner:
			self.chat.send_to_client(client_conn, f"You are not owner of Channel {name}!")
			return

		deleted = self.chat.repo_channel.delete(record.id)
		if not deleted:
			_logger.info(f"user {client_conn.user.username} {client_conn.user.id} "
						 f"try to delete  channel {record.name} {record.id} but something went wrong")
			self.chat.send_to_client(client_conn, f"Channel {record.name} {record.id} could not be deleted")
		else:
			_logger.info(f"user {client_conn.user.username} {client_conn.user.id} delete  channel {record.name} {record.id}")
			self.chat.send_to_client(client_conn, f"Channel {record.name} {record.id} deleted successfully")

	# ---------------------
	# Channel Member Management
	# ---------------------
	def add(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_ADD, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"You cannot add members to Channel {name}, channel does not exist.")
			return
		if record.owner_id != owner:
			self.chat.send_to_client(client_conn, f"You cannot add members to Channel {name}, You are not owner!")
			return
		if not record.members:
			self.chat.send_to_client(client_conn, f"You cannot add members to Channel {name} because channel doesn't have members!")
			return

		users_to_add: list[UserModel] = self._get_members(client_conn, info, add_current_user=False)
		if not users_to_add:
			self.chat.send_to_client(client_conn, f"No members to add supplied for Channel {name}")
			return

		users_to_add_ids = [user.id for user in users_to_add]
		users_current = [member.user_id for member in record.members]
		users_to_add_filtered = set(users_to_add_ids) - set(users_current)

		if not users_to_add_filtered:
			self.chat.send_to_client(client_conn, f"All requested members of Channel {name} are already subscribed")
			return

		self.chat.repo_channel_member.create([{"user_id": user_id, "channel_id": record.id} for user_id in users_to_add_filtered])

		message = f"{len(users_to_add_filtered)} new users joined Channel {name}"
		_logger.info(message)
		self.chat.send_to_client(client_conn, message)

	def remove(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_REMOVE, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"You cannot remove members to Channel {name}, channel does not exist.")
			return
		if record.owner_id != owner:
			self.chat.send_to_client(client_conn, f"You cannot remove members to Channel {name}, You are not owner!")
			return
		if not record.members:
			self.chat.send_to_client(client_conn, f"You cannot remove members to Channel {name} because channel doesn't have members!")
			return

		users_to_remove: list[UserModel] = self._get_members(client_conn, info, add_current_user=False)
		if not users_to_remove:
			self.chat.send_to_client(client_conn, f"No members to remove supplied for Channel {name}")
			return

		users_to_remove_ids = [user.id for user in users_to_remove]
		users_current = [member.user_id for member in record.members]
		users_to_remove_filtered = set(users_to_remove_ids) & set(users_current)

		if not users_to_remove_filtered:
			self.chat.send_to_client(client_conn, f"All requested members of Channel {name} are not subscribed and cannot be removed.")
			return

		deleted_total = 0
		for member_delete_id in users_to_remove_filtered:
			record_id = next((member.id for member in record.members if member.user_id == member_delete_id), None)
			deleted = self.chat.repo_channel_member.delete(record_id)
			deleted_total += int(deleted)

		message = f"{deleted_total} users removed from this Channel {name}"
		_logger.info(message)
		self.chat.send_to_client(client_conn, message)

	def join(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_JOIN, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"You cannot leave Channel {name}, channel does not exist.")
			return
		elif not record.members:
			self.chat.send_to_client(client_conn, f"You cannot leave this channel {name} because channel doesn't have members!")
			return

		for member in record.members:
			if member.user_name == client_conn.user.username:
				self.chat.send_to_client(client_conn, f"You are already a member of Channel {name}!")
				return

		self.chat.repo_channel_member.create({"user_id": owner, "channel_id": record.id})

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} successfully join channel --> {record}")
		self.chat.send_to_client(client_conn, f"You join Channel {name}")

	def leave(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_LEAVE, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"You cannot leave Channel {name}, channel does not exist.")
			return

		if record.owner_id == owner:
			self.chat.send_to_client(client_conn, f"You cannot leave this channel {name} because you are the owner!")
			return
		elif not record.members:
			self.chat.send_to_client(client_conn, f"You cannot leave this channel {name} because channel doesn't have members!")
			return

		for member in record.members:
			if member.user_name == client_conn.user.username:
				member_delete_id = member.id
				break
		else:
			self.chat.send_to_client(client_conn, f"You are not a member of Channel {name}!")
			return

		self.chat.repo_channel_member.delete(member_delete_id)

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} successfully left channel --> {record}")
		self.chat.send_to_client(client_conn, f"You left Channel {name}")

	def _get_data(self, payload: ServerMessageModel) -> tuple[str | int, dict, str]:
		owner = payload.owner.identifier
		info: dict = self.json_decode(payload.body)
		name: str = info["name"]
		return owner, info, name

	def _get_members(self, client_conn, info: dict, add_current_user: bool = True) -> list[UserModel]:
		members: list = [member.strip() for member in info["members"]]
		if add_current_user:
			members.insert(0, client_conn.user.username)

		members_result: list[UserModel] = []
		for member in members:
			user = self.chat.repo_user.get_by_name(member)
			if user:
				members_result.append(user)

		return members_result
