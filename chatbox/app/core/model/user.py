import typing as t
from datetime import datetime
from dataclasses import dataclass

from chatbox.app.core.model.abstract_base_model import BaseModel


@dataclass()
class UserModel(BaseModel):
	username: str
