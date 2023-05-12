import json
import logging
import typing as t

from chatbox.app.core.model.message import ServerInternalMessageModel, ServerMessageModel, MessageRole
from chatbox.app.database.orm.abstract_base_repository import RepositoryBase
from chatbox.app.database.orm.types import Item

_logger = logging.getLogger(__name__)


class MessageRepository(RepositoryBase):
	_table: t.Final[str] = "message"
	_name: t.Final[str] = "owner_name"
	_model: ServerInternalMessageModel = ServerInternalMessageModel

	def create_new_message(self, session_id: int, message: ServerMessageModel) -> ServerInternalMessageModel | None:
		message_json = message.get_struct()

		owner = message_json["owner"]
		sender = message_json["sender"]
		to = message_json["to"]

		to_name = to["name"]
		if to["role"] == MessageRole.ALL.name:
			to_name = to["role"]
			to["name"] = to_name
			to["identifier"] = 1  # super admin identifier

		data = {
			"session_id": session_id,

			"owner_name": owner["name"],
			"from_name": sender["name"],
			"from_role": sender["role"],
			"to_name": to_name,
			"to_role": to["role"],

			"body": message.body,
			"owner": json.dumps(owner),
			"sender": json.dumps(sender),
			"to": json.dumps(to),
		}

		return self.create(data)


	def _build_object(self, data: Item | None) -> ServerInternalMessageModel | None:
		if not data:
			return

		data["owner"] = self._unpack_data(data["id"], data["owner"])
		data["sender"] = self._unpack_data(data["id"], data["sender"])
		data["to"] = self._unpack_data(data["id"], data["to"])
		return super()._build_object(data)

	def _unpack_data(self, _id: str, blob: str) -> dict:
		try:
			return json.loads(blob)
		except (json.JSONDecodeError, TypeError) as error:
			_logger.exception(f"Error while loading session data for {self._table} {_id}, error {error}", exc_info=error)
			return {"error": "__ERROR_LOADING_DATA__"}