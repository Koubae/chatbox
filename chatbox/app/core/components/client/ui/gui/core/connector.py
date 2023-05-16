import threading
import logging
import time
import threading
import types
import typing as t

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

from chatbox.app.core import SocketTCPClient, NetworkSocketException
from chatbox.app.core.components.client import ui
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.client.auth import AuthUser
from chatbox.app.core.components.client.commands import Commands, Command
from chatbox.app.core.components.client.controller.base import ControllerClientException
from chatbox.app.core.components.client.controller.channel import ControllerChannelClient
from chatbox.app.core.components.client.controller.group import ControllerGroupClient
from chatbox.app.core.components.client.controller.message import ControllerMessageClient
from chatbox.app.core.components.client.controller.send_message import ControllerSendToClient
from chatbox.app.core.components.client.controller.users import ControllerUsersClient
from chatbox.app.core.components.commons.controller.base import BaseController, BaseControllerException
from chatbox.app.core.model.message import ServerMessageModel, MessageRole
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)

class ChatBoxThread(threading.Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None, gui: 'ui.gui.app.Gui'):
		super().__init__(group, target, name, args=args, kwargs=kwargs, daemon=daemon)
		self.gui: 'ui.gui.app.Gui' = gui

	def run(self) -> None:
		try:
			super().run()
		except NetworkSocketException as error:
			message_error = f"Chatbox could not connect to server, reason : {error}"
			_logger.warning(message_error)
			self.gui.chatbox_failed_connect = message_error
			self.gui.chat_connector.message_echo(message_error)


class ChatConnector:
	def __init__(self, gui: 'ui.gui.app.Gui', host: str, port: int, user_name: str | None = None, password: str | None = None):
		self.gui: 'ui.gui.app.Gui' = gui
		self.chat: SocketTCPClient = SocketTCPClient(host, port, user_name, password, self)

		self.controller_send_to: ControllerSendToClient = ControllerSendToClient(self.chat, self)
		self.controller_user: ControllerUsersClient = ControllerUsersClient(self.chat, self)
		self.controller_group: ControllerGroupClient = ControllerGroupClient(self.chat, self)
		self.controller_channel: ControllerChannelClient = ControllerChannelClient(self.chat, self)
		self.controller_message: ControllerMessageClient = ControllerMessageClient(self.chat, self)

		self.chatbox_t: ChatBoxThread = ChatBoxThread(target=self.chat, daemon=True, gui=self.gui)
		self.chatbox_t.start()

	# ------------------------------
	# API
	# ------------------------------
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

				case Command.MESSAGE_LIST_SENT | Command.MESSAGE_LIST_RECEIVED:
					self.controller_message.list_user(command)
				case Command.MESSAGE_LIST_GROUP | Command.MESSAGE_LIST_CHANNEL:
					self.controller_message.list_group_or_channel(command, user_input)
				case Command.MESSAGE_DELETE:
					self.controller_message.delete(user_input)

				case Command.ECHO_MESSAGE:
					self.controller_send_to.all(user_input)
				case _:
					self.controller_send_to.all(user_input)

		except ControllerClientException as error:
			if str(error) == "Command target missing":
				return self.message_echo(f"command {command} must contain a target value!")
			return self.message_echo(str(error))

	def message_echo(self, message: str):
		try:
			self.gui.window.logger.log["text"] = message
		except Exception as error:
			_logger.error(f"Error while echoing Chatbox message, error {error}", exc_info=error)

	def message_prompt(self, _: str | None = None) -> str:
		if self.chat.state == objects.Client.LOGGED:
			if not self.gui.window.chat_ui:
				self.gui.window.enter_chat()

			self.gui.window.chat_ui.message_text.wait_variable(self.gui.window.chat_ui.submitted_switch)
			return self.gui.window.chat_ui.current_prompt

		_username = self._request_info("Enter value", "Enter ")
		return _username

	def input_username(self):
		self.gui.window.login.username_entry.wait_variable(self.gui.window.login.submitted_switch)
		return self.gui.window.login.username.get()

	def input_password(self) -> str:
		self.gui.window.login.password_entry.wait_variable(self.gui.window.login.submitted_switch)
		return self.gui.window.login.password.get()

	def message_display(self, payload: ServerMessageModel) -> None:
		owner = payload.owner
		sender = payload.sender

		match sender.role:
			case MessageRole.SERVER:
				return self.message_add("Server", payload.body)
			case MessageRole.GROUP | MessageRole.CHANNEL:
				return self.message_add(f"[{sender.name}] {owner.name} ", payload.body)
			case MessageRole.ALL | _:
				return self.message_add(sender.name, payload.body)

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

	# ------------------------------
	# Additional Functionalities
	# ------------------------------
	def message_add(self, name: str, message: str):
		self.gui.window.chat_ui.messages.add_message(name, message)

	@staticmethod
	def _request_info(title: str, question: str) -> str:
		window_popup = tk.Tk()
		window_popup.withdraw()

		try:
			answer = simpledialog.askstring(title=title, prompt=question, parent=window_popup)
		except Exception as error:
			_logger.error(error)
			raise error
		finally:
			window_popup.destroy()

		if answer:
			return answer
		return ""

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
