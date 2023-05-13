import logging
import typing as t

from chatbox.app.core.model.channel import ChannelModel, ChannelMemberModel
from chatbox.app.database.orm.abstract_base_repository import RepositoryBase
from chatbox.app.database.orm.types import Item, DatabaseOperations

_logger = logging.getLogger(__name__)


class ChannelRepository(RepositoryBase):
	_table: t.Final[str] = "channel"
	_name: t.Final[str] = "name"
	_model: ChannelModel = ChannelModel

	def __init__(self, *args, repo_channel_member: 'ChannelMemberRepository'):
		super().__init__(*args)

		self.repo_channel_member: ChannelMemberRepository = repo_channel_member

	def _build_object(self, data: Item | None) -> ChannelModel | None:
		if not data:
			return

		members: list[ChannelMemberModel] = self.repo_channel_member.list_channel_members(data["id"])
		data["members"] = members
		return super()._build_object(data)

	def list_user_channel(self, owner_id: id) -> list[ChannelModel]:
		where = f"`owner_id` = :owner_id"
		params = {"owner_id": owner_id}

		items = self.get_where(where, params)
		return items


class ChannelMemberRepository(RepositoryBase):
	_table: t.Final[str] = "channel_member"
	_name: t.Final[int] = "user_id"
	_model: ChannelMemberModel = ChannelMemberModel

	_operations: tuple[DatabaseOperations] = (
			DatabaseOperations.READ,
			DatabaseOperations.READ_MANY,
			DatabaseOperations.WRITE_CREATE,
			DatabaseOperations.DELETE,
			DatabaseOperations.DELETE_MANY,
	)

	def list_channel_members(self, channel_id: id) -> list[ChannelMemberModel]:
		where = f"`channel_id` = :channel_id"
		params = {"channel_id": channel_id}

		items = self.get_where(where, params)
		return items
