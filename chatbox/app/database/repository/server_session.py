import logging
import typing as t
import json

from chatbox.app.core.model.server_session import ServerSessionModel
from chatbox.app.database.orm.abstrac_base_repository import RepositoryBase
from chatbox.app.database.orm.sqlite_conn import SQLITEConnectionException
from chatbox.app.database.orm.types import Item


_logger = logging.getLogger(__name__)


class ServerSessionRepository(RepositoryBase):
	_table_name: t.Final[str] = "server_session"

	def get_session(self, _id: int) -> ServerSessionModel | None:	# TODO: move to super class!
		try:
			return self._build_object(self.get("SELECT * FROM server_session WHERE id = :id", {"id": _id}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while get session {_id}, reason {error}")
			return None

	def get_session_by_session_id(self, session_id: str) -> ServerSessionModel | None: 	# TODO: move to super class!
		try:
			return self._build_object(self.get("SELECT * FROM server_session WHERE session_id = :session_id", {"session_id": session_id}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while get session by session_id {session_id}, reason {error}")
			return None

	def list_session(self, limit: int = 100, offset: int = 0) -> list[ServerSessionModel]: # TODO: move to super class!
		try:
			return self._build_objects(self.list("SELECT * FROM server_session LIMIT :limit OFFSET :offset", {"limit": limit, "offset": offset}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while list session, limit = {limit}, offset = {offset}, reason {error}")
			return []

	def create_session(self, session_id: str, data: dict) -> ServerSessionModel | None: # TODO: move to super class!
		data = self._pack_data(session_id, data)

		try:
			return (
				self.create("INSERT INTO server_session (session_id, data) VALUES (:session_id, :data)", ({"session_id": session_id, "data": data},))
				.get_session_by_session_id(session_id)
			)
		except SQLITEConnectionException as error:
			_logger.error(f"Error while creating session {session_id}, reason {error}")
			return None

	def update_session(self, session: ServerSessionModel, data: dict) -> ServerSessionModel | None:  # TODO: move to super class!
		query_data = {
			"id": session.id,
			"data": self._pack_data(session.session_id, data)
		}
		query_data.update(data)
		try:
			return self.update("UPDATE server_session SET data = :data WHERE id = :id", query_data).get_session(session.id)
		except SQLITEConnectionException as error:
			_logger.error(f"Error while updating session {session.id}, reason {error}")
			return None

	def delete_session(self, _id: int) -> bool:  # TODO: move to super class!
		try:
			self.delete("DELETE FROM server_session WHERE id = :id", {"id": _id})
		except SQLITEConnectionException as error:
			_logger.error(f"Error while deleting session {_id}, reason {error}")
			return False
		else:
			return True

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
			_logger.exception(f"Error while building object for table {self._table_name}, reason {error}", exc_info=error)

	@staticmethod
	def _pack_data(session_id: str, data: dict) -> str | None:
		try:
			return json.dumps(data)
		except json.JSONDecodeError as error:
			_logger.exception(f"Error while decoding data for creating session {session_id}, error {error}", exc_info=error)
			return None

	@staticmethod
	def _unpack_data(session_id: str, blob: str) -> dict:
		try:
			return json.loads(blob)
		except (json.JSONDecodeError, TypeError) as error:
			_logger.exception(f"Error while loading session data for session {session_id}, error {error}", exc_info=error)
			return {"error": "__ERROR_LOADING_DATA__"}
