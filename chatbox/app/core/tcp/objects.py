import socket
import dataclasses
import uuid
import typing as t
from typing import NamedTuple, ClassVar
from enum import Enum, auto

from chatbox.app.core.model.user import UserModel


class Address(NamedTuple):
    host: str
    port: int


class MessageDestination(Enum):
    USER = auto()
    GROUP = auto()
    CHANNEL = auto()
    ALL = auto()


SendTo = t.TypedDict("SendTo", {'identifier': int, 'destination': MessageDestination})
Message = t.TypedDict('Message', {'identifier': int, 'message': str, 'send_to': SendTo})
LoginInfo = t.TypedDict('LoginInfo', {'id': t.Optional[int], 'user_name': t.Optional[str], 'password': t.Optional[str], 'user_id': t.Optional[str]})


@dataclasses.dataclass
class Connection:
    """Represents a simple TCP connection, should be used as base class"""
    connection: socket.socket
    identifier: int
    memory_id: int
    address: Address

    def __str__(self):
        return f'{self.address}'


@dataclasses.dataclass
class Client(Connection):
    _user_id: uuid.UUID
    state: str = dataclasses.field(default='PUBLIC')
    user_name: str | None = dataclasses.field(default='PUBLIC_USER')
    login_info: str = dataclasses.field(default=None)
    user: UserModel = dataclasses.field(default=None)
    login_attempts: int = dataclasses.field(default=0)

    PUBLIC: ClassVar[str] = 'PUBLIC'   # TODO: Use enum???
    LOGGED: ClassVar[str] = 'LOGGED'

    def __str__(self):
        return f'{self.user_name} {self.user and f"#{self.user.id}" or ""} ({self.state})'

    def __hash__(self):
        return hash((self.user.id, self.user.username))

    def str_full(self) -> str:
        return f'{self.user_name}{self._user_id} @ {self.address} ({self.state})'

    @property
    def user_id(self) -> str:
        return str(self._user_id)

    @user_id.setter
    def user_id(self, value: uuid.UUID) -> None:
        self._user_id = value

    def set_logged_in(self):
        self.state = Client.LOGGED

    def is_logged(self) -> bool:
        return self.state == Client.LOGGED
