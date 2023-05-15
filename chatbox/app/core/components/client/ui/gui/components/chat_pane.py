import os

import tkinter as tk
from tkinter import ttk

from chatbox.app.core.components.client import ui


class ChatPane(ttk.Notebook):
	def __init__(self, window: 'ui.gui.app.Window'):
		super().__init__(window, style='TNotebook')
		self.app: 'ui.gui.app.Gui' = window.app
		self.window: 'ui.gui.app.Window' = window

		self.__configure_style()

		data = {
			"Users": ["user1", "user2", "user3", "user4", "user5", "user6"],
			"Groups": ["group001", "group001", "group001"],
			"Channels": [f"ch{i}" for i in range(10)],
		}
		panes = ("Users", "Groups", "Channels")
		panes_frames = {}
		for pane in panes:
			_frame = ttk.Frame(self.window, style='Secondary2.TFrame', padding="2 10")
			_frame.grid(row=0, column=1, sticky=tk.N + tk.S, padx=10, pady=1)
			panes_frames[pane] = _frame
			self.add(_frame, text=pane)

			# ----------------------
			# CHAT SELECTION
			# ----------------------

			entities = data[pane]
			for i, entity in enumerate(entities):
				ttk.Button(_frame, text=entity).grid(row=i + 2, column=0, pady=3)

	def __configure_style(self):
		self.grid(row=0, column=0, sticky=tk.N + tk.S, padx=1, pady=1)
		self.grid_rowconfigure(0, weight=1)
