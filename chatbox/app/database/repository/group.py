import logging
import typing as t

from chatbox.app.core.model.group import GroupModel
from chatbox.app.database.orm.abstract_base_repository import RepositoryBase
from chatbox.app.database.orm.types import Item

_logger = logging.getLogger(__name__)


class GroupRepository(RepositoryBase):
	_table: t.Final[str] = "group"
	_name: t.Final[str] = "name"
	_model: GroupModel = GroupModel

	def _build_object(self, data: Item | None) -> GroupModel | None:
		if not data:
			return
		data["members"] = self._unpack_data(data["id"], data["members"])
		return super()._build_object(data)
