import types
import logging

import tkinter as tk

try:
	# windows text blur
	from ctypes import windll  # noqa

	windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
	pass

from chatbox import __version__
from chatbox.app.core.tcp import objects
from chatbox.app.core import SocketTCPClient
from chatbox.app.constants import APP_NAME_CLIENT
from chatbox.app.core.components.client.ui.gui import settings
from chatbox.app.core.components.client.ui.gui.components.window import Window
from chatbox.app.core.components.client.ui.gui.core.connector import ChatConnector


_logger = logging.getLogger(__name__)


class Gui(tk.Tk):
		def __init__(self):
			super().__init__()
			self.username: str = ""

			self.chat: SocketTCPClient | None = None
			self.chat_connector: ChatConnector | None = None
			self.chatbox_failed_connect: str = ""

			self.__configure_app()
			self.window: Window = Window(self)

		def __call__(self, chatbox: SocketTCPClient | None = None, args: tuple | None = None) -> None:
			if chatbox:
				host, port, user_name, password = args
				self.username = user_name
				self.chat_connector: ChatConnector = ChatConnector(self, host, port, user_name, password)
				self.chat: SocketTCPClient = self.chat_connector.chat
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


if __name__ == '__main__':
	app = Gui()
	app()
