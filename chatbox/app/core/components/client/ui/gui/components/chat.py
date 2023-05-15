import os

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # new widget ui
from tkinter import scrolledtext

from chatbox.app.core.components.client import ui
from chatbox.app.core.components.client.ui.gui import settings


class Chat(ttk.Frame):
	def __init__(self, window: 'ui.gui.app.Window'):
		super().__init__(window, style='Chat.TFrame')
		self.app: 'ui.gui.app.App' = window.app
		self.window: 'ui.gui.app.Window' = window
		self.__configure_style()

		self.chatbox_multiline = tk.BooleanVar()
		self.chatbox_multiline.set(settings.CHAT_MULTILINE_ENABLED)


		columns = ('first_name', 'last_name', 'email')
		tree = ttk.Treeview(self, columns=columns, show='headings')

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

		def item_selected(_):
			for selected_item in tree.selection():
				item = tree.item(selected_item)
				record = item['values']
				# show a message
				messagebox.showinfo(title='Information', message=','.join(record))

		tree.bind('<<TreeviewSelect>>', item_selected)
		tree.grid(row=0, column=0, rowspan=2, columnspan=3, sticky=tk.E + tk.W + tk.N + tk.S)
		# add a scrollbar
		scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
		tree.configure(yscroll=scrollbar.set)  # noqa
		scrollbar.grid(row=0, column=2, rowspan=2, sticky=tk.N + tk.S)

		self.message_container = ttk.Frame(self, style="Secondary2.TFrame", padding="2 10 50 50")
		self.message_container.grid(row=2, column=0, columnspan=3, sticky=tk.E + tk.W + tk.N + tk.S)
		self.message_container.rowconfigure(0, weight=1)
		self.message_container.columnconfigure(0, weight=2)
		self.message_container.columnconfigure(1, weight=2)
		self.message_container.columnconfigure(2, weight=0)
		self.message_container.columnconfigure(3, weight=0)

		self.message_text = self.message_text_create_entity()

		self.button_message_submit = ttk.Button(self.message_container, width=10, text="Send", command=lambda: self.message_submit())
		self.button_message_submit.grid(column=2, row=0, padx=0)

		self.button_message_clear = ttk.Button(self.message_container, width=10, text="Clear", style='Danger.TButton',
											   command=lambda: self.message_clear())
		self.button_message_clear.grid(column=3, row=0, padx=0)

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

	def __configure_style(self):
		self.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)

		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=2)
		self.grid_rowconfigure(2, weight=0)

		self.grid_columnconfigure(0, weight=0)
		self.grid_columnconfigure(1, weight=2)
		self.grid_columnconfigure(2, weight=0)

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
