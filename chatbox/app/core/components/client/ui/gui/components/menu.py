import os

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


from chatbox.app.core.components.client import ui


class MenuBase(tk.Menu):
	def __init__(self, window: 'ui.gui.app.Window', cnf=None, **kw):
		super().__init__(window.app, cnf or {}, **kw)
		self.app: 'ui.gui.app.App' = window.app
		self.window: 'ui.gui.app.Window' = window


class MenuHelp(MenuBase):
	def __init__(self, window: 'ui.gui.app.Window', cnf=None, **kw):
		super().__init__(window, cnf or {}, **kw)

		self.add_command(label="Help", command=self.on_help)

	@staticmethod
	def on_help():
		# TODO : Make Proper help
		help_info = """Chat App Client 
- Menu:
	Edit: Chat multiline if enabled allows you to write on multiline, else, when keyboard 'Enter' is pressed the message is sent. Defaults to False.
		
		"""
		messagebox.showinfo(title="Help", message=help_info)


class MenuSettings(MenuBase):
	def __init__(self, window: 'ui.gui.app.Window', cnf=None, **kw):
		super().__init__(window, cnf or {}, **kw)

		self.add_command(label="Exit", background="red", command=self.window.on_close_app)

class MenuEdit(MenuBase):
	def __init__(self, window: 'ui.gui.app.Window', cnf=None, **kw):
		super().__init__(window, cnf or {}, **kw)


		self.window.chatbox_multiline.trace("w", self.on_chatbox_multiline)
		self._menu_chatbox_multiline = tk.Menu(self)
		self._menu_chatbox_multiline.add_radiobutton(
			label="Yes",
			value=True,
			variable=self.window.chatbox_multiline)
		self._menu_chatbox_multiline.add_radiobutton(
			label="No",
			value=False,
			variable=self.window.chatbox_multiline)

		self.add_cascade(label="Chat multiline", menu=self._menu_chatbox_multiline)

	def on_chatbox_multiline(self, *_):
		self.window.message_text.destroy()
		if self.window.chatbox_multiline.get():
			self.window.message_text = self.window.message_text_create_entity()
		else:
			self.window.message_text = self.window.message_text_create_entity()

class MenuMain(MenuBase):
	def __init__(self, window: 'ui.gui.app.Window', cnf=None, **kw):
		super().__init__(window, cnf or {}, **kw)
		self.app.config(menu=self)

		self.menu_edit: MenuEdit = MenuEdit(self.window)
		self.add_cascade(label="Edit", menu=self.menu_edit)
		self.add_separator()

		self.menu_settings: MenuSettings = MenuSettings(self.window)
		self.add_cascade(label="Settings", menu=self.menu_settings)
		self.add_separator()


		self.menu_help: MenuHelp = MenuHelp(self.window)
		self.add_cascade(label="Help", menu=self.menu_help)
		self.add_separator()


