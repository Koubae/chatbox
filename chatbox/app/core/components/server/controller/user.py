import logging
import json

from chatbox.app.core.components.commons.controller.base import BaseController
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.model.message import ServerMessageModel
from chatbox.app.core.model.user import UserModel
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class ControllerUsers(BaseController):

	def list_(self, client_conn: objects.Client, payload: ServerMessageModel, action: _c.Codes) -> None:
		_c.remove_chat_code_from_payload(action, payload)  # noqa

		match action:
			case _c.Codes.USER_LIST_LOGGED:
				items: list[UserModel] = self.chat.repo_user.users_logged(list(self.chat.clients_identified.keys()))
			case _c.Codes.USER_LIST_UN_LOGGED:
				items: list[UserModel] = self.chat.repo_user.users_un_logged(list(self.chat.clients_identified.keys()))
			case _:
				items: list[UserModel] = self.chat.repo_user.get_many()

		group_names = [item.to_json_small() for item in items]
		self.chat.send_to_client(client_conn, _c.make_message(action, json.dumps(group_names)))
