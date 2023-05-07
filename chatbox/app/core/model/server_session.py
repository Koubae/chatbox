import typing as t
import uuid
import copy
from dataclasses import dataclass, field

from chatbox.app.core.model.abstract_base_model import BaseModel
from chatbox.app.core.model.user import UserModel


class ServerSession(t.TypedDict, total=False):
	users: dict[str, str]


SERVER_SESSION_DEFAULT: ServerSession = {
	"users": {}
}


@dataclass
class ServerSessionModel(BaseModel):
	session_id: str
	data: t.Optional[dict] = field(default=None, repr=False, hash=False, compare=False)

	@staticmethod
	def create_session_id() -> str:
		return str(uuid.uuid4())

	@staticmethod
	def create_session_data() -> ServerSession:
		return copy.deepcopy(SERVER_SESSION_DEFAULT)

	def get_user_from_session(self, username: str) -> int | None:
		user_id = self.data["users"].get(username, None)
		if not user_id:
			return None
		return int(user_id)

	def add_user(self, user: UserModel) -> None:
		self.data["users"][user.username] = str(user.id)
