import logging
import json

from chatbox.app.core.components.commons.controller.base import BaseController
from chatbox.app.constants import chat_internal_codes as _c
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
				items: list[ServerInternalMessageModel] = self.chat.repo_message
			case _c.Codes.MESSAGE_LIST_CHANNEL:
				items: list[ServerInternalMessageModel] = self.chat.repo_message
			case _c.Codes.MESSAGE_LIST_SENT | _:
				items: list[ServerInternalMessageModel] = self.chat.repo_message.get_many_sent(client_conn.user.username)

		group_names = [item.to_json_small() for item in items]
		self.chat.send_to_client(client_conn, _c.make_message(action, json.dumps(group_names)))

	def delete(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.MESSAGE_DELETE, payload)  # noqa