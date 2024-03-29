import logging
import typing as t
from datetime import datetime
import json

from chatbox.app.constants import SERVER_SESSION_TIME_SECONDS
from chatbox.app.core.model.server_session import ServerSessionModel
from chatbox.app.core.model.user import UserModel
from chatbox.app.database.orm.abstract_base_repository import RepositoryBase
from chatbox.app.database.orm.sqlite_conn import SQLITEConnectionException
from chatbox.app.database.orm.types import Item


_logger = logging.getLogger(__name__)


class ServerSessionRepository(RepositoryBase):
	_table: t.Final[str] = "server_session"
	_name: t.Final[str] = "session_id"
	_model: ServerSessionModel = ServerSessionModel

	def create(self, data: t.Iterable[dict] | dict) -> ServerSessionModel | None:
		data["data"] = self._pack_data(data["session_id"], data["data"])
		return super().create(data)

	def create_new_session(self) -> ServerSessionModel | None:
		return self.create({"session_id": ServerSessionModel.create_session_id(), "data": ServerSessionModel.create_session_data()})

	def update(self,  _id: int, data: dict) -> ServerSessionModel | None:
		if "data" in data:
			data["data"] = self._pack_data(_id, data["data"])
		return super().update(_id, data)

	def _build_object(self, data: Item | None) -> ServerSessionModel | None:
		if not data:
			return
		data["data"] = self._unpack_data(data["session_id"], data["data"])
		return super()._build_object(data)

	def get_session_or_create(self) -> ServerSessionModel | None:
		try:
			session = self._build_object(self.db.get("SELECT * FROM server_session ORDER BY created DESC LIMIT 1"))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while get last session {self._table}, reason {error}")
			return None

		if not session:
			_logger.info(f"Session not found, creating new session")
			session = self.create_new_session()
		else:
			last_session_seconds = int((datetime.utcnow() - session.modified).total_seconds())
			if last_session_seconds > SERVER_SESSION_TIME_SECONDS:
				_logger.info(f"Last session has expired {last_session_seconds} seconds ago, creating new session")
				session = self.create_new_session()

		return session

	def add_user_to_session(self, session: ServerSessionModel, user: UserModel) -> ServerSessionModel:
		session.add_user(user)
		session_updated = self.update(session.id, {"data": session.data})
		return session_updated or session

	def remove_user_to_session(self, session: ServerSessionModel, user: UserModel) -> ServerSessionModel:
		session.remove_user(user)
		session_updated = self.update(session.id, {"data": session.data})
		return session_updated or session

	@staticmethod
	def _pack_data(_id: str | int, data: dict) -> str | None:
		try:
			return json.dumps(data)
		except json.JSONDecodeError as error:
			_logger.exception(f"Error while decoding data for creating session {_id}, error {error}", exc_info=error)
			return None
