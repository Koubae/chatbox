import logging
import json

from chatbox.app.core.components.commons.controller.base import BaseController
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.model.channel import ChannelModel
from chatbox.app.core.model.group import GroupModel
from chatbox.app.core.model.message import ServerMessageModel, ServerInternalMessageModel
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class ControllerMessage(BaseController):

	def list_(self, client_conn: objects.Client, payload: ServerMessageModel, action: _c.Codes) -> None:
		_c.remove_chat_code_from_payload(action, payload)  # noqa

		match action:
			case _c.Codes.MESSAGE_LIST_RECEIVED:
				items: list[ServerInternalMessageModel] = self.chat.repo_message.get_many_received(client_conn.user.username)
			case _c.Codes.MESSAGE_LIST_GROUP:
				name: str = self._get_item_name(payload)

				record: GroupModel = self.chat.repo_group.get_by_name(name)
				if not record:
					self.chat.send_to_client(client_conn, f"You cannot list messages to Group {name}, channel does not exist.")
					return
				is_member = record.is_member(client_conn.user.username)
				if not is_member:
					self.chat.send_to_client(client_conn, f"You cannot list messages to Group {name}, your are not a member")
					return

				items: list[ServerInternalMessageModel] = self.chat.repo_message.get_many_group(name)
			case _c.Codes.MESSAGE_LIST_CHANNEL:
				name: str = self._get_item_name(payload)

				record: ChannelModel = self.chat.repo_channel.get_by_name(name)
				if not record:
					self.chat.send_to_client(client_conn, f"You cannot list messages to Channel {name}, channel does not exist.")
					return
				is_member = record.is_member(client_conn.user.id)
				if not is_member:
					self.chat.send_to_client(client_conn, f"You cannot list messages to Channel {name}, your are not a member")
					return

				items: list[ServerInternalMessageModel] = self.chat.repo_message.get_many_channel(name)

			case _c.Codes.MESSAGE_LIST_SENT | _:
				items: list[ServerInternalMessageModel] = self.chat.repo_message.get_many_sent(client_conn.user.username)

		group_names = [item.to_json_small() for item in items]
		self.chat.send_to_client(client_conn, _c.make_message(action, json.dumps(group_names)))

	def delete(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.MESSAGE_DELETE, payload)  # noqa

	def _get_item_name(self, payload: ServerMessageModel) -> str:
		data: dict = self.json_decode(payload.body)
		name: str = data["name"]
		return name