from getpass import getpass

from chatbox.app.core import tcp


# TODO: Improve printing
class Terminal:

	def __init__(self, chat: 'tcp.SocketTCPClient'):
		self.chat: 'tcp.SocketTCPClient' = chat

	def message_echo(self, message: str, destination: None = None): # todo Add message destination?
		print(message)

	def message_prompt(self, prompt: str | None = None) -> str:
		value = input(prompt and prompt or '')
		print('\033[1A' + '\033[K', end='')  # erase text that user typed
		return value

	def input_username(self) -> str:
		return self.message_prompt(">>> Enter user name: ")

	def input_password(self) -> str:
		return getpass(">>> Enter Password: ")
