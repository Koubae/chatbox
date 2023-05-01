from dataclasses import dataclass, field

from chatbox.app.core.model.abstract_base_model import BaseModel


@dataclass
class UserModel(BaseModel):
	username: str
	password: str = field(repr=False, hash=False, compare=False)


@dataclass
class UserLoginModel(BaseModel):
	user_id: int
	session_id: int
	attempts: int
