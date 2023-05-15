import os

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from chatbox.app.core.components.client import ui


class ChatMessages(ttk.Treeview):
	COLUMNS: tuple[str] = ('first_name', 'last_name', 'email')

	def __init__(self, window: 'ui.gui.app.Window', chat: 'ui.gui.components.Chat'):
		super().__init__(chat, columns=ChatMessages.COLUMNS, show='headings')
		self.app: 'ui.gui.app.App' = window.app
		self.window: 'ui.gui.app.Window' = window
		self.chat: 'ui.gui.components.Chat' = chat

		self.__configure_style()

		for col in ChatMessages.COLUMNS:
			self.heading(col, text=" ".join(col.split("_")).capitalize())

		contacts = []
		for n in range(1, 100):
			contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))

		# add data to the treeview
		for contact in contacts:
			self.insert('', 0, values=contact)

		def item_selected(_):
			for selected_item in self.selection():
				item = self.item(selected_item)
				record = item['values']
				# show a message
				messagebox.showinfo(title='Information', message=','.join(record))

		self.bind('<<TreeviewSelect>>', item_selected)

	def __configure_style(self):
		self.grid(row=0, column=0, rowspan=2, columnspan=3, sticky=tk.E + tk.W + tk.N + tk.S)
		# add a scrollbar
		scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.yview)
		self.configure(yscroll=scrollbar.set)  # noqa
		scrollbar.grid(row=0, column=2, rowspan=2, sticky=tk.N + tk.S)
