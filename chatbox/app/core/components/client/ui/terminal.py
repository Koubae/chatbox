import json
from getpass import getpass

from chatbox.app.core import tcp
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.client.auth import AuthUser
from chatbox.app.core.components.client.commands import Command, Commands
from chatbox.app.core.components.client.controller.base import ControllerClientException
from chatbox.app.core.components.client.controller.group import ControllerGroupClient
from chatbox.app.core.components.client.controller.send_message import ControllerSendToClient
from chatbox.app.core.model.message import ServerMessageModel, MessageRole


class Terminal:

	def __init__(self, chat: 'tcp.SocketTCPClient'):
		self.chat: 'tcp.SocketTCPClient' = chat

		self.controller_send_to: ControllerSendToClient = ControllerSendToClient(self.chat, self)
		self.controller_group: ControllerGroupClient = ControllerGroupClient(self.chat, self)

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
				case Command.QUIT:
					self.chat.quit()
				case Command.LOGOUT:
					AuthUser.logout(self.chat)

				case Command.SEND_TO_ALL:
					self.controller_send_to.all()
				case Command.SEND_TO_CHANNEL:
					...
				case Command.SEND_TO_GROUP:
					self.controller_send_to.group(user_input)
				case Command.SEND_TO_USER:
					self.controller_send_to.user(user_input)
				case Command.USER_LIST_ALL:
					...
				case Command.USER_LIST_LOGGED:
					...
				case Command.USER_LIST_UN_LOGGED:
					...

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

				case Command.CHANNEL_LIST_ALL:
					...
				case Command.CHANNEL_LIST_JOINED:
					...
				case Command.CHANNEL_LIST_UN_JOINED:
					...
				case Command.CHANNEL_CREATE:
					...
				case Command.CHANNEL_UPDATE:
					...
				case Command.CHANNEL_ADD:
					...
				case Command.CHANNEL_JOIN:
					...
				case Command.CHANNEL_DELETE:
					...

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

	def display_groups(self, payload: ServerMessageModel) -> None:
		_c.remove_chat_code_from_payload(_c.Codes.GROUP_LIST, payload)  # noqa

		groups = json.loads(payload.body)
		self.message_echo(f"These are groups you own:\n\n")
		for group in groups:
			group['members'] = group['members'][:10]  # Hack in terminal ui, print_table don't look nice when there is too much data in one cell
		self.print_table(groups)
		self.message_echo("\n")

	def print_table(self, data):
		columns = list(data[0].keys() if data else [])

		table = [columns] + [[str(row.get(col, '')) for col in columns] for row in data]
		column_size = [max(map(len, col)) for col in zip(*table)]

		format_string = ' | '.join(["{{:<{}}}".format(i) for i in column_size])

		header_separator = ['-' * i for i in column_size]
		table.insert(1, header_separator)  # Header Separators line
		for item in table:
			self.message_echo(format_string.format(*item))
