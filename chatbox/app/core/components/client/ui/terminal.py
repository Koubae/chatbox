from getpass import getpass

from chatbox.app.core import tcp
from chatbox.app.core.components.client.auth import AuthUser
from chatbox.app.core.components.client.commands import Command, Commands
from chatbox.app.core.components.commons.functions import get_command_target
from chatbox.app.core.model.message import ServerMessageModel, MessageRole


class Terminal:

	def __init__(self, chat: 'tcp.SocketTCPClient'):
		self.chat: 'tcp.SocketTCPClient' = chat

	@staticmethod
	def message_echo(message: str):
		print(message)

	def message_display(self, payload: ServerMessageModel): # TODO: send from to --> user , group , channel
		owner = payload.owner
		sender = payload.sender

		if sender.role is MessageRole.SERVER:
			name = f"[SERVER] -->"
		elif sender.role not in (MessageRole.USER, MessageRole.ALL):
			name = f"[{sender.name}] $ {owner.name} -->"
		else:
			name = f"$ {sender.name} -->"

		message = f'{name} {payload.body}'
		self.message_echo(message)

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
		match command:
			case Command.QUIT:
				self.chat.quit()
			case Command.LOGOUT:
				AuthUser.logout(self.chat)
			case Command.SEND_TO_ALL:
				...
			case Command.SEND_TO_CHANNEL:
				...
			case Command.SEND_TO_GROUP:
				...
			case Command.SEND_TO_USER:
				user = get_command_target(user_input)
				if not user:
					return self.chat.ui.message_echo(f"command {Command.SEND_TO_USER} must contain user name!")
				user_input = self.message_prompt(f"@{user} : ")
				self.chat.send_to_user(user, user_input)

			case Command.USER_LIST_ALL:
				...
			case Command.USER_LIST_LOGGED:
				...
			case Command.USER_LIST_UN_LOGGED:
				...

			case Command.GROUP_LIST:
				...
			case Command.GROUP_CREATE:
				...
			case Command.GROUP_UPDATE:
				...
			case Command.GROUP_LEAVE:
				...
			case Command.GROUP_DELETE:
				...

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
				self.chat.send_to_all(user_input)
			case _:
				self.chat.send_to_all(user_input)
