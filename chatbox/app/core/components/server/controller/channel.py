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

		channels: list[ChannelModel] = self.chat.repo_channel.list_user_channel(client_conn.user.id)

		items = [item.to_json() for item in channels]
		self.chat.send_to_client(client_conn, _c.make_message(_c.Codes.CHANNEL_LIST_ALL, json.dumps(items)))

	def create(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_CREATE, payload)  # noqa

		owner, info, name = self._get_data(payload)
		members: list[UserModel] = self._get_members(client_conn, info)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if record:
			self.chat.send_to_client(client_conn, f"Group {name} already exists!")
			return
		record: ChannelModel = self.chat.repo_channel.create({"name": name, "owner_id": owner})
		if not record:
			self.chat.send_to_client(client_conn, f"Error while creating channel {name}!")
			return

		self.chat.repo_channel_member.create([{"user_id": user.id, "channel_id": record.id}  for user in members])

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} created new channel --> {record} with {len(members)} members!")
		self.chat.send_to_client(client_conn, f"Group {name} created successfully")

	def update(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_UPDATE, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"Group {name} cannot be created, channel does not exist.")
			return

		members: list[UserModel] = self._get_members(client_conn, info)


		record: ChannelModel = self.chat.repo_channel.update(record.id,
														{"name": name, "owner_id": owner, "members": json.dumps(members)})
		if not record:
			self.chat.send_to_client(client_conn, f"Error while updating channel {name}!")
			return

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} updated channel --> {record}")
		self.chat.send_to_client(client_conn, f"Group {name} updated successfully")

	def delete(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_DELETE, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"Group {name} cannot be deleted, channel does not exist.")
			return

		if record.owner_id != owner:
			self.chat.send_to_client(client_conn, f"You are not owner of Group {name}!")
			return

		deleted = self.chat.repo_channel.delete(record.id)
		if not deleted:
			_logger.info(f"user {client_conn.user.username} {client_conn.user.id} "
						 f"try to delete  channel {record.name} {record.id} but something went wrong")
			self.chat.send_to_client(client_conn, f"Group {record.name} {record.id} could not be deleted")
		else:
			_logger.info(f"user {client_conn.user.username} {client_conn.user.id} delete  channel {record.name} {record.id}")
			self.chat.send_to_client(client_conn, f"Group {record.name} {record.id} deleted successfully")

	def leave(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.CHANNEL_LEAVE, payload)  # noqa

		owner, info, name = self._get_data(payload)

		record: ChannelModel = self.chat.repo_channel.get_by_name(name)
		if not record:
			self.chat.send_to_client(client_conn, f"You cannot a Group {name}, channel does not exist.")
			return

		if record.owner_id == owner:
			self.chat.send_to_client(client_conn, f"You cannot leave this channel {name} because you are the owner!")
			return

		user_to_remove: str = client_conn.user.username
		if client_conn.user.username not in record.members:
			self.chat.send_to_client(client_conn, f"You are not a member of Group {name}!")
			return

		members_current = set(record.members)
		member_to_remove = {user_to_remove}
		members_updated = members_current - member_to_remove

		record: ChannelModel = self.chat.repo_channel.update(record.id,{"members": json.dumps(list(members_updated))})
		if not record:
			self.chat.send_to_client(client_conn, f"Error while leaving channel {name}!")
			return

		_logger.info(f"user {client_conn.user.username} {client_conn.user.id} successfully left channel --> {record}")
		self.chat.send_to_client(client_conn, f"You left Group {name}")

	def _get_data(self, payload: ServerMessageModel) -> tuple[str | int, dict, str]:
		owner = payload.owner.identifier
		info: dict = self.json_decode(payload.body)
		name: str = info["name"]
		return owner, info, name

	def _get_members(self, client_conn, info: dict) -> list[UserModel]:
		members: list = [member.strip() for member in info["members"]]
		members.insert(0, client_conn.user.username)

		members_result: list[UserModel] = []
		for member in members:
			user = self.chat.repo_user.get_by_name(member)
			if user:
				members_result.append(user)

		return members_result
