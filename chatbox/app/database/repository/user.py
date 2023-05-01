import logging
import typing as t

from chatbox.app.core.model.user import UserModel, UserLoginModel
from chatbox.app.database.orm.abstract_base_repository import RepositoryBase
from chatbox.app.database.orm.types import DatabaseOperations

_logger = logging.getLogger(__name__)


class UserRepository(RepositoryBase):
	_table: t.Final[str] = "user"
	_name: t.Final[str] = "username"
	_model: UserModel = UserModel


class UserLoginRepository(RepositoryBase):
	_table: t.Final[str] = "user_login"
	_name: t.Final[int] = "user_id"
	_model: UserLoginModel = UserLoginModel

	_operations: tuple[DatabaseOperations] = (
			DatabaseOperations.READ,
			DatabaseOperations.READ_MANY,
			DatabaseOperations.WRITE_CREATE,
			DatabaseOperations.DELETE,
			DatabaseOperations.DELETE_MANY,
		)
