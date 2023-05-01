import logging
import typing as t
import json

from chatbox.app.core.model.server_session import ServerSessionModel
from chatbox.app.database.orm.abstrac_base_repository import RepositoryBase
from chatbox.app.database.orm.types import Item


_logger = logging.getLogger(__name__)


class ServerSessionRepository(RepositoryBase):
	_table: t.Final[str] = "server_session"
	_name: t.Final[str] = "session_id"

	_columns = ["session_id", "data"]   # TODO: make dynamic

	def create(self, data: t.Iterable[dict] | dict) -> ServerSessionModel | None:
		data["data"] = self._pack_data(data["session_id"], data["data"])
		return super().create(data)

	def update(self,  _id: int, data: dict) -> ServerSessionModel | None:
		if "data" in data:
			data["data"] = self._pack_data(_id, data["data"])
		return super().update(_id, data)

	def _build_object(self, data: Item | None) -> ServerSessionModel | None:
		if not data:
			return
		_id = data["id"]
		session_id = data["session_id"]
		session_data = self._unpack_data(session_id, data["data"])

		try:
			return ServerSessionModel(
				_id,
				data["created"],
				data["modified"],
				session_id,
				session_data
			)
		except KeyError as error:
			_logger.exception(f"Error while building object for table {self._table}, reason {error}", exc_info=error)

	@staticmethod
	def _pack_data(_id: str | int, data: dict) -> str | None:
		try:
			return json.dumps(data)
		except json.JSONDecodeError as error:
			_logger.exception(f"Error while decoding data for creating session {_id}, error {error}", exc_info=error)
			return None

	@staticmethod
	def _unpack_data(session_id: str, blob: str) -> dict:
		try:
			return json.loads(blob)
		except (json.JSONDecodeError, TypeError) as error:
			_logger.exception(f"Error while loading session data for session {session_id}, error {error}", exc_info=error)
			return {"error": "__ERROR_LOADING_DATA__"}
