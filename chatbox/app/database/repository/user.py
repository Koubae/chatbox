import logging
import typing as t

from chatbox.app.core.model.user import UserModel
from chatbox.app.database.orm.abstrac_base_repository import RepositoryBase
from chatbox.app.database.orm.types import Item


_logger = logging.getLogger(__name__)


class UserRepository(RepositoryBase):
	_table_name: t.Final[str] = "user"

	def create_new_user(self, username: str, password: str) -> UserModel | None:
		return (self.create("INSERT INTO user (username, password) VALUES (:username, :password)",({"username": username, "password": password},))
			.get_user(username)
		)

	def get_user(self, username: str) -> UserModel | None:
		return self._build_object(self.get("SELECT * FROM user WHERE username = :username", {"username": username}))

	def list_users(self, limit: int, offset: int) -> list[UserModel]:
		return self._build_objects(self.get("SELECT * FROM user LIMIT :limit OFFSET :offset", {"limit": limit, "offset": offset}))

	def update_user(self, username: str): ...
	def delete_user(self, username: str): ...

	def _build_object(self, data: Item | None) -> UserModel | None:
		if not data:
			return

		try:
			return UserModel(
				data["id"],
				data["created"],
				data["modified"],
				data["username"]
			)
		except KeyError as error:
			_logger.exception(f"Error while building object for table {self._table_name}, reason {error}", exc_info=error)
