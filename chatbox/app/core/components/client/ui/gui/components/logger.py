import os

import tkinter as tk
from tkinter import ttk

from chatbox.app.core.components.client import ui


class Logger(ttk.Frame):
	def __init__(self, window: 'ui.gui.app.Window'):
		super().__init__(window, style='Chat.TFrame', padding="0 10 10 50")
		self.app: 'ui.gui.app.Gui' = window.app
		self.window: 'ui.gui.app.Window' = window

		self.__configure_style()

		self.log = ttk.Label(self, text="", style='dark.TLabel')
		self.log.pack(fill=tk.X, expand=True)

	def __configure_style(self):
		self.grid(row=1, column=0, columnspan=2,  sticky="new", padx=10, pady=0)
