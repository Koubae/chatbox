import time
import threading
import types

import tkinter as tk
from tkinter import messagebox

from chatbox.app.core import SocketTCPClient
from chatbox.app.core.components.client.auth import AuthUser
from chatbox.app.core.components.client.commands import Commands, Command
from chatbox.app.core.components.client.controller.base import ControllerClientException
from chatbox.app.core.components.client.controller.channel import ControllerChannelClient
from chatbox.app.core.components.client.controller.group import ControllerGroupClient
from chatbox.app.core.components.client.controller.message import ControllerMessageClient
from chatbox.app.core.components.client.controller.send_message import ControllerSendToClient
from chatbox.app.core.components.client.controller.users import ControllerUsersClient
from chatbox.app.core.model.message import ServerMessageModel, MessageRole
from chatbox.app.core.tcp import objects

try:
	# windows text blur
	from ctypes import windll  # noqa

	windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
	pass

from chatbox import __version__
from chatbox.app.core.components.client.ui.gui.components.window import Window
from chatbox.app.constants import APP_NAME_CLIENT
from chatbox.app.core.components.client.ui.gui import settings
from tkinter import simpledialog
import logging

_logger = logging.getLogger(__name__)


class Gui(tk.Tk):
	def __init__(self):
		super().__init__()
		self.chat = None
		self.chatbox_t: threading.Thread | None = None

		self.__configure_app()
		self.window: Window = Window(self)

	def __call__(self, chatbox: SocketTCPClient | None = None, args: tuple | None = None) -> None:
		if chatbox:
			host, port, user_name, password = args
			self.chat: SocketTCPClient = SocketTCPClient(host, port, user_name, password, self)

			self.controller_send_to: ControllerSendToClient = ControllerSendToClient(self.chat, self)
			self.controller_user: ControllerUsersClient = ControllerUsersClient(self.chat, self)
			self.controller_group: ControllerGroupClient = ControllerGroupClient(self.chat, self)
			self.controller_channel: ControllerChannelClient = ControllerChannelClient(self.chat, self)
			self.controller_message: ControllerMessageClient = ControllerMessageClient(self.chat, self)

			self.chatbox_t = threading.Thread(target=self.chat, daemon=True)
			self.chatbox_t.start()
		else:
			# build a fake chat
			self.chat = types.SimpleNamespace()
			self.chat.state = objects.Client.LOGGED

		if self.chat and self.chat.state == objects.Client.LOGGED:
			self.window.enter_chat()

		self.mainloop()

	def __configure_app(self):
		self.title(f'{APP_NAME_CLIENT} - v{__version__.__version__} {__version__.__build__}')

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self.attributes('-zoomed', True)
		self.attributes('-topmost', 1)

		self.configure(background=settings.COLOR_PRIMARY_9)
		self.option_add('*Dialog.msg.width', 150)
		self.option_add('*Dialog.msg.height', 80)
		self.option_add("*Dialog.msg.wrapLength", "18i")

	# -------------------------------
	# API
	# -------------------------------
	def message_echo(self, message: str):
		self.window.logger.log["text"] = message

	def message_add(self, name: str, message: str):
		self.window.chat.messages.add_message(name, message)

	def message_display(self, payload: ServerMessageModel) -> None:
		owner = payload.owner
		sender = payload.sender
		_logger.info("paaf fdiusplas ", payload.body)

		match sender.role:
			case MessageRole.SERVER:
				return self.message_add("Server", payload.body)
			case MessageRole.GROUP | MessageRole.CHANNEL:
				return self.message_add(f"[{sender.name}] {owner.name} ", payload.body)
			case MessageRole.ALL | _:
				return self.message_add(sender.name, payload.body)

	def input_password(self) -> str:
		_password = self._request_info("Password", "Enter your password: ")
		return _password

	def input_username(self):
		_username = self._request_info("Username", "Enter your username: ")
		return _username

	def message_prompt(self, _: str | None = None) -> str:
		if self.chat.state == objects.Client.LOGGED:
			if not self.window.chat:
				self.window.enter_chat()

			self.window.chat.message_text.wait_variable(self.window.chat.submitted_switch)
			return self.window.chat.current_prompt

		_username = self._request_info("Enter value", "Enter ")
		return _username

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

	def _request_info(self, title: str, question: str) -> str:
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


if __name__ == '__main__':
	app = Gui()
	app()
