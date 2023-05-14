from dataclasses import dataclass, field

from chatbox.app.constants import DATETIME_DEFAULT
from chatbox.app.core.model.abstract_base_model import BaseModel


@dataclass
class UserModel(BaseModel):
	username: str
	password: str = field(repr=False, hash=False, compare=False)

	def to_json(self) -> dict:
		return {
			'id': self.id,
			'name': self.username,
			'created': self.created.strftime(DATETIME_DEFAULT),
			'modified': self.modified.strftime(DATETIME_DEFAULT),
		}

	def to_json_small(self) -> dict:
		return {
			'id': self.id,
			'name': self.username
		}


@dataclass
class UserLoginModel(BaseModel):
	user_id: int
	session_id: int
	attempts: int
