import os

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from chatbox.app.constants import APP_NAME_CLIENT
from chatbox.app.core.components.client import ui
from chatbox.app.core.components.client.ui.gui.components.chat import Chat

from chatbox.app.core.components.client.ui.gui.components.logger import Logger
from chatbox.app.core.components.client.ui.gui.components.login import Login
from chatbox.app.core.components.client.ui.gui.components.menu import MenuMain
from chatbox.app.core.components.client.ui.gui import settings


class Window(ttk.Frame):
	def __init__(self, master: 'ui.gui.app.Gui'):
		super().__init__()
		self.app: 'ui.gui.app.Gui' = master
		self.window_width = self.app.winfo_screenwidth()
		self.window_height = self.app.winfo_screenheight()
		self.window_fullscreen: bool = False
		self.style = ttk.Style()

		self.__register_events_hotkeys()
		self.__configure_style()

		# ----------------------
		# Components
		# ----------------------
		self.logger: Logger = Logger(self)

		self.chat_ui: Chat | None = None
		self.menu: MenuMain | None = None

		self.login = Login(self)

	def enter_chat(self):
		self.style.configure('TLabel', background=settings.DEFAULT_2, fieldbackground=settings.DEFAULT_2, foreground='black')
		self.chat_ui = Chat(self)
		self.menu: MenuMain = MenuMain(self)
		self.login.destroy()

	# --------------------------
	# EVENTS: Hotkeys
	# --------------------------
	def action_show_on_help(self, _=None):
		self.menu.menu_help.on_help()

	def action_chatbox_multiline_switch(self, _=None):
		self.chat_ui.chatbox_multiline.set(not self.chat_ui.chatbox_multiline.get())

	def action_full_screen(self, _=None):
		self.window_fullscreen = not self.window_fullscreen
		self.app.attributes("-fullscreen", self.window_fullscreen)

	def action_full_screen_out(self, _=None):
		self.window_fullscreen = False
		self.app.attributes("-fullscreen", False)

	def on_close_app(self):
		response = messagebox._show(  # noqa
			"Warning",
			f"You are about to close {APP_NAME_CLIENT}, are you sure?",
			messagebox.WARNING,
			messagebox.YESNOCANCEL,
		)
		if response == "yes":
			self.app.chatbox_closed = True
			self.app.chat.terminate()
			self.app.chat_connector.stop_waiting()
			self.app.destroy()

	def __register_events_hotkeys(self):
		self.app.bind("<F1>", self.action_show_on_help)
		self.app.bind("<F2>", self.action_chatbox_multiline_switch)
		self.app.bind("<F11>", self.action_full_screen)
		self.app.bind("<Escape>", self.action_full_screen_out)

	def __configure_style(self):
		self.style.theme_use("default")
		# configure it to the background you want
		self.style.configure('Main.TFrame', background=settings.COLOR_SECONDARY_9, foreground="white")
		self.style.configure('Chat.TFrame', background=settings.COLOR_SECONDARY_9, foreground="white")
		self.style.configure('Secondary.TFrame', background=settings.COLOR_SECONDARY_9)
		self.style.configure('Secondary2.TFrame', background=settings.COLOR_SECONDARY)
		self.style.configure('Primary.TFrame', background=settings.COLOR_PRIMARY)
		self.style.configure('Default2.TFrame', background=settings.DEFAULT_1)

		self.style.configure('TButton', background=settings.COLOR_PRIMARY, foreground='white', width=20, borderwidth=3, focusthickness=3,
							 focuscolor='none')
		self.style.map('TButton', background=[('active', settings.COLOR_PRIMARY_9), ('pressed', settings.COLOR_PRIMARY_10)])
		self.style.map("Danger.TButton",
					   background=[("active", settings.DANGER), ("!active", settings.DANGER_LIGHT)],
					   foreground=[("active", "white"), ("!active", "black")])
		self.style.map("Secondary.TButton",
					   background=[("active", settings.COLOR_SECONDARY_9), ("!active", settings.COLOR_SECONDARY)],
					   foreground=[("active", "white"), ("!active", "white")])

		self.style.configure(".", font=('Helvetica', 12), foreground="white")
		self.style.configure("Treeview", background=settings.COLOR_SECONDARY_9, fieldbackground=settings.COLOR_SECONDARY_9, foreground='white')
		self.style.configure("Treeview.Heading", background=settings.COLOR_PRIMARY_9, foreground='white')

		self.style.configure('TLabel', background=settings.COLOR_SECONDARY, fieldbackground=settings.COLOR_SECONDARY, foreground='white')
		self.style.configure('dark.TLabel', background=settings.COLOR_SECONDARY_9, fieldbackground=settings.COLOR_SECONDARY_9, foreground='white',
							 font=('Roboto', 8, 'italic'))

		self.style.configure('TEntry', font=('Helvetica', 16, 'italic'),
							 fieldbackground=settings.COLOR_SECONDARY_9, foreground='white', width=20, height=10, borderwidth=3, focusthickness=3, focuscolor='none')
		self.style.configure("Chat.TEntry", fieldbackground=settings.COLOR_SECONDARY_9, foreground="white")

		self.style.configure("vertical.TNotebook", tabposition='n',
							 background=settings.COLOR_SECONDARY_9,
							 focuscolor=settings.COLOR_PRIMARY,
							 bordercolor=settings.COLOR_SECONDARY_9
							 )

		self.config(style='Main.TFrame')
		self.app.config(background=settings.COLOR_SECONDARY_9)
		self.grid(column=0, row=0, sticky=tk.N + tk.W + tk.E + tk.S)

		self.grid_columnconfigure(1, weight=2)

		self.grid_rowconfigure(0, weight=2)
		self.grid_rowconfigure(1, weight=0)
