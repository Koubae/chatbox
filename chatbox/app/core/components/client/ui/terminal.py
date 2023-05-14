import time
import typing as t

from getpass import getpass

from chatbox.app.core import tcp
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.client.auth import AuthUser
from chatbox.app.core.components.client.commands import Command, Commands
from chatbox.app.core.components.client.controller.base import ControllerClientException
from chatbox.app.core.components.client.controller.channel import ControllerChannelClient
from chatbox.app.core.components.client.controller.group import ControllerGroupClient
from chatbox.app.core.components.client.controller.message import ControllerMessageClient
from chatbox.app.core.components.client.controller.send_message import ControllerSendToClient
from chatbox.app.core.components.client.controller.users import ControllerUsersClient
from chatbox.app.core.components.commons.controller.base import BaseController, BaseControllerException
from chatbox.app.core.model.message import ServerMessageModel, MessageRole


class Terminal:

	def __init__(self, chat: 'tcp.SocketTCPClient'):
		self.chat: 'tcp.SocketTCPClient' = chat

		self.controller_send_to: ControllerSendToClient = ControllerSendToClient(self.chat, self)
		self.controller_user: ControllerUsersClient = ControllerUsersClient(self.chat, self)
		self.controller_group: ControllerGroupClient = ControllerGroupClient(self.chat, self)
		self.controller_channel: ControllerChannelClient = ControllerChannelClient(self.chat, self)
		self.controller_message: ControllerMessageClient = ControllerMessageClient(self.chat, self)

	@staticmethod
	def message_echo(message: str):
		print(message)

	@staticmethod
	def message_prompt(prompt: str | None = None) -> str:
		value = input(prompt and prompt or '')
		print('\033[1A' + '\033[K', end='')  # erase text that user typed
		return value

	def input_username(self) -> str:
		return self.message_prompt(">>> Enter user name: ")

	@staticmethod
	def input_password() -> str:
		return getpass(">>> Enter Password: ")

	def next_command(self):
		user_input = self.message_prompt()
		command = Commands.read_command(user_input)

		try:
			match command:
				case Command.LOGIN | Command.IDENTIFICATION | Command.IDENTIFICATION_REQUIRED | Command.LOGIN_SUCCESS | Command.LOGIN_CREATED:
					self.chat.ui.message_echo("Waiting logging in, please wait...")  # <-- Must not perform any action!
					time.sleep(1)
					return
				case Command.QUIT:
					self.chat.quit()
				case Command.LOGOUT:
					AuthUser.logout(self.chat)

				case Command.SEND_TO_ALL:
					self.controller_send_to.all()
				case Command.SEND_TO_CHANNEL:
					self.controller_send_to.channel(user_input)
				case Command.SEND_TO_GROUP:
					self.controller_send_to.group(user_input)
				case Command.SEND_TO_USER:
					self.controller_send_to.user(user_input)

				case Command.USER_LIST_ALL | Command.USER_LIST_LOGGED | Command.USER_LIST_UN_LOGGED:
					self.controller_user.list_(command)

				case Command.GROUP_LIST:
					self.controller_group.list_()
				case Command.GROUP_CREATE:
					self.controller_group.create(user_input)
				case Command.GROUP_UPDATE:
					self.controller_group.update(user_input)
				case Command.GROUP_DELETE:
					self.controller_group.delete(user_input)
				case Command.GROUP_LEAVE:
					self.controller_group.leave(user_input)

				case Command.CHANNEL_LIST_ALL | Command.CHANNEL_LIST_OWNED | Command.CHANNEL_LIST_JOINED | Command.CHANNEL_LIST_UN_JOINED:
					self.controller_channel.list_(command)
				case Command.CHANNEL_CREATE:
					self.controller_channel.create(user_input)
				case Command.CHANNEL_UPDATE:
					self.controller_channel.update(user_input)
				case Command.CHANNEL_DELETE:
					self.controller_channel.delete(user_input)
				case Command.CHANNEL_ADD | Command.CHANNEL_REMOVE:
					self.controller_channel.member_management(user_input, command)
				case Command.CHANNEL_JOIN | Command.CHANNEL_LEAVE:
					self.controller_channel.member_request(user_input, command)

				case Command.MESSAGE_LIST_SENT | Command.MESSAGE_LIST_RECEIVED | Command.MESSAGE_LIST_GROUP | Command.MESSAGE_LIST_CHANNEL:
					self.controller_message.list_(command)
				case Command.MESSAGE_DELETE:
					self.controller_message.delete(user_input)

				case Command.ECHO_MESSAGE:
					self.controller_send_to.all(user_input)
				case _:
					self.controller_send_to.all(user_input)

		except ControllerClientException as error:
			if str(error) == "Command target missing":
				return self.chat.ui.message_echo(f"command {command} must contain a target value!")
			return self.chat.ui.message_echo(str(error))

	def message_display(self, payload: ServerMessageModel) -> None:
		owner = payload.owner
		sender = payload.sender

		match sender.role:
			case MessageRole.SERVER:
				name = f"[SERVER] -->"
			case MessageRole.GROUP:
				name = f"[{sender.name}] $ {owner.name} -->"
			case MessageRole.CHANNEL:
				name = f"[{sender.name}] $ {owner.name} -->"
			case MessageRole.ALL | _:
				name = f"$ {sender.name} -->"

		message = f'{name} {payload.body}'
		self.message_echo(message)

	def display_users(self, code: _c.Codes, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(code, payload)  # noqa
		self._display_table_csv_type("users", payload)

	def display_groups(self, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.GROUP_LIST, payload)  # noqa
		self._display_table_csv_type("groups", payload, add_members=True)

	def display_channels(self, code: _c.Codes, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(code, payload)  # noqa
		self._display_table_box_type("channels", payload)

	def display_messages(self, code: _c.Codes, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(code, payload)  # noqa
		self._display_table_csv_type("messages", payload)

	def _display_table_csv_type(self, _type: str, payload: ServerMessageModel, add_members: bool = False) -> None:
		if not payload.body:
			self.message_echo(f"No {_type} to display")
			return

		try:
			items = BaseController.json_decode(payload.body)
		except BaseControllerException as error:
			self.message_echo(f"Error while decoding Server response, reason : {error}")
		else:
			if not items:
				self.message_echo(f"No {_type} to display")
				return
			self.message_echo(f"These are {_type}:\n\n")
			if add_members:
				for item in items:
					item['members'] = item['members'][:10]  # Hack in terminal ui, print_table don't look nice when there is too much data in one cell
			self.print_table(items)
			self.message_echo("\n")

	def _display_table_box_type(self, _type: str, payload: ServerMessageModel) -> None:
		if not payload.body:
			self.message_echo(f"No {_type} to display")
			return

		try:
			items = BaseController.json_decode(payload.body)
		except BaseControllerException as error:
			self.message_echo(f"Error while decoding Server response, reason : {error}")
		else:
			if not items:
				self.message_echo(f"No {_type} to display")
				return
			self.message_echo(f"These are {_type}:\n\n")
			self.print_box(items)
			self.message_echo("\n")

	def print_table(self, data) -> None:
		columns = list(data[0].keys() if data else [])

		table = [columns] + [[str(row.get(col, '')) for col in columns] for row in data]
		column_size = [max(map(len, col)) for col in zip(*table)]

		format_string = ' | '.join(["{{:<{}}}".format(i) for i in column_size])

		header_separator = ['-' * i for i in column_size]
		table.insert(1, header_separator)  # Header Separators line
		for item in table:
			self.message_echo(format_string.format(*item))

	def print_box(self, items: list[dict]) -> None:
		spacing = 30

		self.message_echo("")
		for item in items:
			list_objects: list[tuple[str, t.Iterable[dict]]] = []
			name = item.get("name", None)
			if name:
				self.message_echo("-" * spacing)
				self.message_echo(f"{name:>{int(spacing / 2)}}")
				self.message_echo("-" * spacing)
			self.message_echo("")
			for key, value in item.items():
				if isinstance(value, (list, tuple, set)):
					list_objects.append((key, value))
					continue
				self.message_echo(f"- {key}: {value}")

			for key, value in list_objects:
				self.message_echo(f"- {key}: ")
				for entry in value:
					data = [str(value) for value in entry.values()]
					self.message_echo(f"\t- {', '.join(data)}")

			self.message_echo("\n" + "=" * (spacing * 2) + "\n")
