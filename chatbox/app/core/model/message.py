import json
import typing as t
import logging
from dataclasses import dataclass, field
from enum import Enum, auto

from chatbox.app.core.model.abstract_base_model import BaseModel


_logger = logging.getLogger(__name__)


class MessageRole(Enum):
	USER = auto()
	SERVER = auto()
	GROUP = auto()
	CHANNEL = auto()
	ALL = auto()


class MessageDestination(t.NamedTuple):
	identifier: str | int
	name: str
	role: MessageRole

	users: list[str] = []


@dataclass
class MessageModel(BaseModel):
	body: str
	sender: MessageDestination
	to: MessageDestination

	def __post_init__(self):
		if isinstance(self.sender, dict):
			self.sender = MessageDestination(self.sender["identifier"], self.sender["name"], self.sender["role"])
		if isinstance(self.to, dict):
			self.to = MessageDestination(self.to["identifier"], self.to["name"], self.to["role"])

		if not isinstance(self.sender.role, MessageRole):
			self.sender = MessageDestination(self.sender.identifier, self.sender.name, MessageRole[self.sender.role])  # noqa
		if not isinstance(self.to.role, MessageRole):
			self.to = MessageDestination(self.to.identifier, self.to.name, MessageRole[self.to.role])  # noqa

	@classmethod
	def new_message(cls, sender: MessageDestination, _to: MessageDestination, body: str) -> t.Self:
		new_message: MessageModel = cls(
			id=-1,
			created=None,   # noqa
			modified=None,  # noqa
			body=body,
			sender=sender,
			to=_to
		)

		return 	new_message

	@classmethod
	def from_json(cls, payload: str) -> t.Self | None:
		try:
			message_loaded = json.loads(payload)
		except (json.JSONDecodeError, ValueError, TypeError) as error:
			_logger.exception(f"Error while loadin json message {payload[:255]}, reason {error}", exc_info=error)
			return None
		else:
			return cls(**message_loaded)

	def to_json(self) -> str:
		return json.dumps({
			"id": self.id,
			"created": self.created,
			"modified": self.modified,
			"body": self.body,
			"sender": {
				"identifier": self.sender.identifier,
				"name": self.sender.name,
				"role": self.sender.role.name,
			},
			"to": {
				"identifier": self.to.identifier,
				"name": self.to.name,
				"role": self.to.role.name,
			},
		})


@dataclass
class ServerMessageModel(MessageModel):
	owner: MessageDestination = field(default=None)

	def __post_init__(self):
		super().__post_init__()
		if isinstance(self.owner, dict):
			self.owner = MessageDestination(self.owner["identifier"], self.owner["name"], self.owner["role"])

	@classmethod
	def new_message(cls, owner: MessageDestination, sender: MessageDestination, _to: MessageDestination, body: str) -> t.Self:  # noqa
		new_message: MessageModel = cls(
			id=-1,
			created=None,  # noqa
			modified=None,  # noqa
			body=body,
			sender=sender,
			to=_to,
			owner=owner,
		)

		return new_message

	def get_struct(self) -> dict:
		return {
			"id": self.id,
			"created": self.created,
			"modified": self.modified,
			"body": self.body,
			"owner": {
				"identifier": self.owner.identifier,
				"name": self.owner.name,
				"role": self.owner.role.name,
			},
			"sender": {
				"identifier": self.sender.identifier,
				"name": self.sender.name,
				"role": self.sender.role.name,
			},
			"to": {
				"identifier": self.to.identifier,
				"name": self.to.name,
				"role": self.to.role.name,
			},
		}

	def to_json(self) -> str:
		return json.dumps(self.get_struct())


@dataclass
class ServerInternalMessageModel(BaseModel):
	session_id: int

	owner_name: str
	from_name: str
	from_role: str
	to_name: str
	to_role: str

	body: str
	owner: MessageDestination
	sender: MessageDestination
	to: MessageDestination

	def __post_init__(self):
		if isinstance(self.sender, dict):
			self.sender = MessageDestination(self.sender["identifier"], self.sender["name"], self.sender["role"])
		if isinstance(self.to, dict):
			self.to = MessageDestination(self.to["identifier"], self.to["name"], self.to["role"])
		if isinstance(self.owner, dict):
			self.owner = MessageDestination(self.owner["identifier"], self.owner["name"], self.owner["role"])

		if not isinstance(self.sender.role, MessageRole):
			self.sender = MessageDestination(self.sender.identifier, self.sender.name, MessageRole[self.sender.role])  # noqa
		if not isinstance(self.to.role, MessageRole):
			self.to = MessageDestination(self.to.identifier, self.to.name, MessageRole[self.to.role])  # noqa
		if not isinstance(self.owner.role, MessageRole):
			self.owner = MessageDestination(self.owner.identifier, self.owner.name, MessageRole[self.owner.role])  # noqa