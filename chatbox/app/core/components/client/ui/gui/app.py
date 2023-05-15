import tkinter as tk

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


class Gui(tk.Tk):
	def __init__(self):
		super().__init__()
		self.__configure_app()
		self.window: Window = Window(self)

	def __call__(self) -> None:
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
