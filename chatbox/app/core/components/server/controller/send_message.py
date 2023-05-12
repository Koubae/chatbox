import logging

from chatbox.app.core.components.server.controller.base import BaseController
from chatbox.app.core.model.message import MessageDestination, ServerMessageModel, MessageRole
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class ControllerSendTo(BaseController):

	def user(self): ...
	def group(self): ...
	def channel(self): ...

	def all(self, client_conn: objects.Client, payload: ServerMessageModel):
		payload.to = MessageDestination(identifier=payload.owner.identifier, name=payload.owner.name, role=MessageRole.ALL)
		self.chat.add_message_to_broadcast(client_conn, payload)
