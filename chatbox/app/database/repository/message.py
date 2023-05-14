import json
import logging
import typing as t

from chatbox.app.core.model.message import ServerInternalMessageModel, ServerMessageModel, MessageRole
from chatbox.app.database.orm.abstract_base_repository import RepositoryBase
from chatbox.app.database.orm.types import Item, DatabaseOperations

_logger = logging.getLogger(__name__)


class MessageRepository(RepositoryBase):
	_table: t.Final[str] = "message"
	_name: t.Final[str] = "owner_name"
	_model: ServerInternalMessageModel = ServerInternalMessageModel

	_operations: tuple[DatabaseOperations] = (
		DatabaseOperations.READ,
		DatabaseOperations.READ_MANY,
		DatabaseOperations.WRITE_CREATE,
		DatabaseOperations.DELETE,
		DatabaseOperations.DELETE_MANY,
	)

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


	def get_many_received(self, username: str, limit: int = 100, offset: int = 0) -> list[ServerInternalMessageModel]:
		query = f"SELECT * FROM message WHERE to_name = :to_name OR (to_name = 'ALL' AND to_role = 'ALL') ORDER BY ID DESC LIMIT :limit OFFSET :offset"

		items = self.get_many_raw(query, {"to_name": username, "limit": limit, "offset": offset})
		return items

	def get_many_sent(self, username: str, limit: int = 100, offset: int = 0) -> list[ServerInternalMessageModel]:
		query = f"SELECT * FROM message WHERE owner_name = :owner_name ORDER BY ID DESC LIMIT :limit OFFSET :offset"

		items = self.get_many_raw(query, {"owner_name": username, "limit": limit, "offset": offset})
		return items

	def get_many_group(self, name: str, limit: int = 100, offset: int = 0) -> list[ServerInternalMessageModel]:
		query = f"SELECT * FROM message WHERE from_role = 'GROUP' AND from_name = :name ORDER BY ID DESC LIMIT :limit OFFSET :offset"

		items = self.get_many_raw(query, {"name": name, "limit": limit, "offset": offset})
		return items
