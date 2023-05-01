import typing as t
import uuid
from dataclasses import dataclass, field

from chatbox.app.core.model.abstract_base_model import BaseModel


@dataclass
class ServerSessionModel(BaseModel):
	session_id: str
	data: t.Optional[dict] = field(default=None, repr=False, hash=False, compare=False)

	@staticmethod
	def create_session_id() -> str:
		return str(uuid.uuid4())
