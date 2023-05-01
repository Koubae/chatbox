import logging
import typing as t

from chatbox.app.core.model.user import UserModel
from chatbox.app.database.orm.abstrac_base_repository import RepositoryBase
from chatbox.app.database.orm.types import Item


_logger = logging.getLogger(__name__)


class UserRepository(RepositoryBase):
	_table: t.Final[str] = "user"
	_name: t.Final[str] = "username"

	_columns = ["username", "password"]   # TODO: make dynamic

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
			_logger.exception(f"Errowhile building object for table {self._table}, reason {error}", exc_info=error)
