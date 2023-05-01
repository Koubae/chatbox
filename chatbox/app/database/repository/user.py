import logging
import typing as t

from chatbox.app.core.model.user import UserModel
from chatbox.app.database.orm.abstrac_base_repository import RepositoryBase


_logger = logging.getLogger(__name__)


class UserRepository(RepositoryBase):
	_table: t.Final[str] = "user"
	_name: t.Final[str] = "username"
	_model: UserModel = UserModel
