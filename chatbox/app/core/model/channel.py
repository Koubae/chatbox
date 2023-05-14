import logging
from dataclasses import dataclass

from chatbox.app.constants import DATETIME_DEFAULT
from chatbox.app.core.model.abstract_base_model import BaseModel


_logger = logging.getLogger(__name__)


@dataclass
class ChannelMemberModel(BaseModel):
	user_id: int
	user_name: str
	channel_id: int

	def to_json(self) -> dict:
		return {
			'id': self.id,
			'user_id': self.user_id,
			'user_name': self.user_name,
			'channel_id': self.channel_id,
			'created': self.created.strftime(DATETIME_DEFAULT),
			'modified': self.modified.strftime(DATETIME_DEFAULT),
		}

	def to_json_related(self) -> dict:
		return {
			'id': self.id,
			'user_id': self.user_id,
			'user_name': self.user_name,
		}

@dataclass
class ChannelModel(BaseModel):
	name: str
	owner_id: id
	members: list[ChannelMemberModel]

	def __str__(self):
		return f"Channel {self.name} created by {self.owner_id}, members {self.members}"

	def to_json(self) -> dict:
		return {
			'id': self.id,
			'name': self.name,
			'owner_id': self.owner_id,
			'members': [member.to_json_related() for member in self.members],
			'created': self.created.strftime(DATETIME_DEFAULT),
			'modified': self.modified.strftime(DATETIME_DEFAULT),
		}
