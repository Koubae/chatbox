import os

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # new widget ui
from tkinter import scrolledtext

from chatbox.app.constants import APP_NAME_CLIENT
from chatbox.app.core.components.client import ui
from chatbox.app.core.components.client.ui.gui.components.chat_pane import ChatPane
from chatbox.app.core.components.client.ui.gui.components.menu import MenuMain
from chatbox.app.core.components.client.ui.gui import settings


class Window(ttk.Frame):
	def __init__(self, master: 'ui.gui.app.App'):
		super().__init__()
		self.app: 'ui.gui.app.App' = master
		self.window_width = self.app.winfo_screenwidth()
		self.window_height = self.app.winfo_screenheight()
		self.window_fullscreen: bool = False
		self.style = ttk.Style()

		self.__register_events_hotkeys()
		self.__configure_style()

		# ----------------------
		# Components
		# ----------------------
		self.chatbox_multiline = tk.BooleanVar()
		self.chatbox_multiline.set(settings.CHAT_MULTILINE_ENABLED)

		# menu
		self.menu: MenuMain = MenuMain(self)
		self.chat_pane = ChatPane(self)

		# ----------------------
		# CHAT
		# ----------------------

		self.chat = ttk.Frame(self, style='Chat.TFrame')
		self.chat.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)

		self.chat.grid_rowconfigure(0, weight=1)
		self.chat.grid_rowconfigure(1, weight=2)
		self.chat.grid_rowconfigure(2, weight=0)

		self.chat.grid_columnconfigure(0, weight=0)
		self.chat.grid_columnconfigure(1, weight=2)
		self.chat.grid_columnconfigure(2, weight=0)


		columns = ('first_name', 'last_name', 'email')
		tree = ttk.Treeview(self.chat, columns=columns, show='headings')

		tree.heading('first_name', text='First Name')
		tree.heading('last_name', text='Last Name')
		tree.heading('email', text='Email')

		# generate sample data
		contacts = []
		for n in range(1, 100):
			contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))

		# add data to the treeview
		for contact in contacts:
			tree.insert('', 0, values=contact)

		def item_selected(event):
			for selected_item in tree.selection():
				item = tree.item(selected_item)
				record = item['values']
				# show a message
				messagebox.showinfo(title='Information', message=','.join(record))

		tree.bind('<<TreeviewSelect>>', item_selected)
		tree.grid(row=0, column=0, rowspan=2, columnspan=3, sticky=tk.E + tk.W + tk.N + tk.S)
		# add a scrollbar
		scrollbar = ttk.Scrollbar(self.chat, orient=tk.VERTICAL, command=tree.yview)
		tree.configure(yscroll=scrollbar.set)  # noqa
		scrollbar.grid(row=0, column=2, rowspan=2, sticky=tk.N + tk.S)

		self.message_container = ttk.Frame(self.chat, style="Secondary2.TFrame", padding="2 10 50 50")
		self.message_container.grid(row=2, column=0, columnspan=3, sticky=tk.E + tk.W + tk.N + tk.S)
		self.message_container.rowconfigure(0, weight=1)
		self.message_container.columnconfigure(0, weight=2)
		self.message_container.columnconfigure(1, weight=2)
		self.message_container.columnconfigure(2, weight=0)
		self.message_container.columnconfigure(3, weight=0)

		self.message_text = self.message_text_create_entity()

		self.button_message_submit = ttk.Button(self.message_container, width=10, text="Send", command=lambda: self.message_submit())
		self.button_message_submit.grid(column=2, row=0, padx=0)

		self.button_message_clear = ttk.Button(self.message_container, width=10, text="Clear", style='Danger.TButton', command=lambda: self.message_clear())
		self.button_message_clear.grid(column=3, row=0, padx=0)

	# --------------------------
	# EVENTS: Hotkeys
	# --------------------------
	def action_full_screen(self, _=None):
		self.window_fullscreen = not self.window_fullscreen
		self.app.attributes("-fullscreen", self.window_fullscreen)

	def action_full_screen_out(self, _=None):
		self.window_fullscreen = False
		self.app.attributes("-fullscreen", False)

	# --------------------------
	# EVENTS: Button Callbacks
	# --------------------------
	def message_submit(self) -> str:
		if self.chatbox_multiline.get():
			message = self.message_text.get("1.0", tk.END)
			if "\n" == message[0]:  # Remove first char if is empty space
				message = message[1:]
		else:
			message = self.message_text.get()  # noqa

		message_removed_last_char = message
		self.message_clear()
		return message_removed_last_char

	def message_clear(self) -> None:
		if self.chatbox_multiline.get():
			self.message_text.delete('1.0', tk.END)
		else:
			self.message_text.delete('0', tk.END)

	def on_close_app(self):
		response = messagebox._show(  # noqa
			"Warning",
			f"You are about to close {APP_NAME_CLIENT}, are you sure?",
			messagebox.WARNING,
			messagebox.YESNOCANCEL,
		)
		if response == "yes":
			self.master.destroy()

	def __register_events_hotkeys(self):
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
		self.style.configure("Treeview", background=settings.COLOR_SECONDARY_9, foreground='white')
		self.style.configure("Treeview.Heading", background=settings.COLOR_PRIMARY_9, foreground='white')

		self.style.configure('TEntry', font=('Times New Roman', 14, 'italic'),
							 fieldbackground="white", foreground='black', width=20, height=5, borderwidth=3, focusthickness=3, focuscolor='none')
		self.style.configure("Chat.TEntry", fieldbackground=settings.COLOR_SECONDARY_9, foreground="white")

		self.style.configure("vertical.TNotebook", tabposition='n',
							 background=settings.COLOR_SECONDARY_9,
							 focuscolor=settings.COLOR_PRIMARY,
							 bordercolor=settings.COLOR_SECONDARY_9
							 )

		self.config(style='Main.TFrame')
		self.grid(column=0, row=0, sticky=tk.N + tk.W + tk.E + tk.S)

		self.grid_columnconfigure(1, weight=2)
		self.grid_rowconfigure(0, weight=1)

	def message_text_create_entity(self) -> ttk.Entry | scrolledtext.ScrolledText:
		if self.chatbox_multiline.get():
			message_text = self._create_message_text_multi_line()
		else:
			message_text = self._create_message_text_single_line()
			message_text.bind("<Return>", lambda _: self.message_submit())

		message_text.focus()
		message_text.grid(row=0, column=0, columnspan=2, sticky=tk.E + tk.W + tk.N + tk.S, padx=10)

		return message_text

	def _create_message_text_single_line(self) -> ttk.Entry:
		return ttk.Entry(self.message_container, style="Chat.TEntry", width=45, font=('Times New Roman', 14, 'italic'))

	def _create_message_text_multi_line(self) -> scrolledtext.ScrolledText:
		return scrolledtext.ScrolledText(self.message_container, width=40, height=5, font=('Times New Roman', 14, 'italic'),
										 background=settings.COLOR_SECONDARY_9, foreground="white")
