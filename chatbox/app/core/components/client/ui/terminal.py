from getpass import getpass

from chatbox.app.core import tcp
from chatbox.app.core.components.client.ui.commands import Command, Commands, Codes


# TODO: Improve printing
class Terminal:

	def __init__(self, chat: 'tcp.SocketTCPClient'):
		self.chat: 'tcp.SocketTCPClient' = chat

	def message_echo(self, message: str, destination: None = None): # todo Add message destination?
		command = Commands.read_command(message)

		match command:
			case Command.QUIT:
				...
			case Command.LOGIN:
				...
			case Command.LOGOUT:
				...

			case Command.SEND_TO_ALL:
				...
			case Command.SEND_TO_CHANNEL:
				...
			case Command.SEND_TO_GROUP:
				...
			case Command.SEND_TO_USER:
				...

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

			case Command.ECHO_MESSAGE, _:
				print(message)


	def message_prompt(self, prompt: str | None = None) -> str:
		value = input(prompt and prompt or '')
		print('\033[1A' + '\033[K', end='')  # erase text that user typed
		return value

	def input_username(self) -> str:
		return self.message_prompt(">>> Enter user name: ")

	def input_password(self) -> str:
		return getpass(">>> Enter Password: ")
