import logging
from dataclasses import dataclass

from chatbox.app.core.model.abstract_base_model import BaseModel


_logger = logging.getLogger(__name__)


@dataclass
class GroupModel(BaseModel):
	name: str
	owner_id: id
	members: list

	def __str__(self):
		return f"Group {self.name} created by {self.owner_id}, members {self.members}"
