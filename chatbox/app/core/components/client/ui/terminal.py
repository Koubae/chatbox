import json
from getpass import getpass

from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.client.auth import AuthUser
from chatbox.app.core.components.client.commands import Command, Commands
from chatbox.app.core.components.commons.controller.base import BaseController
from chatbox.app.core.components.commons.functions import get_command_target
from chatbox.app.core.model.message import ServerMessageModel, MessageRole


class CommandTerminateException(Exception):
	pass


class Terminal(BaseController):
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
					...
				case Command.SEND_TO_CHANNEL:
					...
				case Command.SEND_TO_GROUP:
					...
				case Command.SEND_TO_USER:
					user = get_command_target(user_input)
					if not user:
						raise CommandTerminateException("Command target missing")

					user_input = self.message_prompt(f"@{user} : ")
					self.chat.send_to_user(user, user_input)

				case Command.USER_LIST_ALL:
					...
				case Command.USER_LIST_LOGGED:
					...
				case Command.USER_LIST_UN_LOGGED:
					...

				case Command.GROUP_LIST:
					group_command = _c.make_message(_c.Codes.GROUP_LIST, _c.Codes.GROUP_CREATE.name)
					self.chat.send_to_server(group_command)
				case Command.GROUP_CREATE:
					group_info = get_command_target(user_input)
					if not group_info:
						raise CommandTerminateException("Command target missing")

					group_name, *group_members = group_info.split(" ")
					group_members = list(set(group_members) - {self.chat.user_name})
					if not group_members:
						raise CommandTerminateException("Groups members are required when creating a new group")

					payload = {"name": group_name, "members": group_members}
					group_command = _c.make_message(_c.Codes.GROUP_CREATE, json.dumps(payload))
					self.chat.send_to_server(group_command)
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

		except CommandTerminateException as error:
			if str(error) == "Command target missing":
				return self.chat.ui.message_echo(f"command {command} must contain a target value!")
			return self.chat.ui.message_echo(str(error))

	def message_display(self, payload: ServerMessageModel) -> None:
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

	def display_groups(self, payload: ServerMessageModel) -> None:
		self._remove_chat_code_from_payload(_c.Codes.GROUP_LIST, payload)  # noqa

		groups = json.loads(payload.body)
		self.message_echo(f"These are groups you own:\n\n")
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
