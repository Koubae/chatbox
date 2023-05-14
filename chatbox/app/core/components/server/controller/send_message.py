import logging

from chatbox.app.core.components.commons.controller.base import BaseController
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.model.channel import ChannelModel
from chatbox.app.core.model.group import GroupModel
from chatbox.app.core.model.message import MessageDestination, ServerMessageModel, MessageRole
from chatbox.app.core.model.user import UserModel
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class ControllerSendTo(BaseController):

	def user(self, client_conn: objects.Client, payload: ServerMessageModel):
		_c.remove_chat_code_from_payload(_c.Codes.SEND_TO_USER, payload)

		destination = payload.to.identifier
		user: UserModel | None = self.chat.repo_user.get_by_name(destination)
		if not user:
			self.chat.send_to_client(client_conn, f"user {destination} does not exist!")
			return

		payload.to = MessageDestination(identifier=user.id, name=user.username, role=MessageRole.USER)
		self.chat.add_message_to_broadcast(client_conn, payload)

	def user_this(self, client_conn: objects.Client, payload: ServerMessageModel):
		"""Sends a message to the current client_conn user"""
		payload.to = MessageDestination(identifier=client_conn.user.id, name=client_conn.user.username, role=MessageRole.USER)
		self.chat.add_message_to_broadcast(client_conn, payload)

	def group(self, client_conn: objects.Client, payload: ServerMessageModel):
		_c.remove_chat_code_from_payload(_c.Codes.SEND_TO_GROUP, payload)

		destination = payload.to.identifier
		group: GroupModel | None = self.chat.repo_group.get_by_name(destination)
		if not group:
			self.chat.send_to_client(client_conn, f"group {destination} does not exist!")
			return

		owner_name = payload.owner.name
		is_member = False
		for user_name in group.members:
			if user_name == owner_name:
				is_member = True
		if not is_member:
			self.chat.send_to_client(client_conn, f"user {owner_name} is not a member of {group.name}")
			return

		payload.sender = MessageDestination(identifier=group.id, name=group.name, role=MessageRole.GROUP)
		payload.to = MessageDestination(identifier=group.id, name=group.name, role=MessageRole.GROUP, users=group.members)
		self.chat.add_message_to_broadcast(client_conn, payload)

	def channel(self, client_conn: objects.Client, payload: ServerMessageModel):
		_c.remove_chat_code_from_payload(_c.Codes.SEND_TO_CHANNEL, payload)

		destination = payload.to.identifier
		channel: ChannelModel | None = self.chat.repo_channel.get_by_name(destination)
		if not channel:
			self.chat.send_to_client(client_conn, f"channel {destination} does not exist!")
			return

		owner_name = payload.owner.name
		is_member = False
		member_usernames = []
		for member in channel.members:
			member_usernames.append(member.user_name)
			if member.user_name == owner_name:
				is_member = True

		if not is_member:
			self.chat.send_to_client(client_conn, f"user {owner_name} is not a member of {channel.name}")
			return

		payload.sender = MessageDestination(identifier=channel.id, name=channel.name, role=MessageRole.CHANNEL)
		payload.to = MessageDestination(identifier=channel.id, name=channel.name, role=MessageRole.CHANNEL, users=member_usernames)
		self.chat.add_message_to_broadcast(client_conn, payload)

	def all(self, client_conn: objects.Client, payload: ServerMessageModel):
		payload.to = MessageDestination(identifier=payload.owner.identifier, name=payload.owner.name, role=MessageRole.ALL)
		self.chat.add_message_to_broadcast(client_conn, payload)
