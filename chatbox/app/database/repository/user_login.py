import logging
import typing as t

from chatbox.app.core.model.user import UserModel, UserLoginModel
from chatbox.app.database.orm.abstract_base_repository import RepositoryBase
from chatbox.app.database.orm.sqlite_conn import SQLITEConnectionException
from chatbox.app.database.orm.types import Item


_logger = logging.getLogger(__name__)


class UserLoginRepository(RepositoryBase):
	_table: t.Final[str] = "user_login"
	_name: t.Final[str] = "user_login"

	_columns = ["user_id", "session_id", "attempts"]   # TODO: make dynamic

	def get(self, _id: int) -> UserLoginModel | None:  # TODO
		try:
			return self._build_object(self.get("SELECT * FROM user_login WHERE id = :id", {"id": _id}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while get {self._table} - {_id}, reason {error}")
			return None

	def get_user_by_username(self, username: str) -> UserModel | None:
		try:
			return self._build_object(self.db.get("SELECT * FROM user WHERE username = :username", {"username": username}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while get user by username {username}, reason {error}")
			return None

	def list_users(self, limit: int = 100, offset: int = 0) -> list[UserModel]:
		try:
			return self._build_objects(self.list("SELECT * FROM user LIMIT :limit OFFSET :offset", {"limit": limit, "offset": offset}))
		except SQLITEConnectionException as error:
			_logger.error(f"Error while list users, limit = {limit}, offset = {offset}, reason {error}")
			return []

	def create_new_user(self, username: str, password: str) -> UserModel | None:
		try:
			return (
				self.create("INSERT INTO user (username, password) VALUES (:username, :password)", ({"username": username, "password": password},))
				.get_user_by_username(username)
			)
		except SQLITEConnectionException as error:
			_logger.error(f"Error while creating new user {username}, reason {error}")
			return None

	def update_user(self, user: UserModel, data: dict) -> UserModel | None:
		query_data = {
			"id": user.id,
			"username": user.username
		}
		query_data.update(data)
		try:
			return self.update("UPDATE user SET username = :username WHERE id = :id", query_data).get(user.id)
		except SQLITEConnectionException as error:
			_logger.error(f"Error while updating user {user.id}, reason {error}")
			return None

	def delete_user(self, _id: int) -> bool:
		try:
			self.delete("DELETE FROM user WHERE id = :id", {"id": _id})
		except SQLITEConnectionException as error:
			_logger.error(f"Error while deleting user {_id}, reason {error}")
			return False
		else:
			return True

	def _build_object(self, data: Item | None) -> UserModel | None:
		if not data:
			return

		try:
			return UserModel(
				data["id"],
				data["created"],
				data["modified"],
				data["username"],
				data["password"],
			)
		except KeyError as error:
			_logger.exception(f"Error while building object for table {self._table}, reason {error}", exc_info=error)
