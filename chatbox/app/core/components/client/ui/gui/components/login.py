import os

import tkinter as tk
from tkinter import ttk

from chatbox.app.core.components.client import ui


class Login(ttk.Frame):
	def __init__(self, window: 'ui.gui.app.Window'):
		super().__init__(window, style='Chat.TFrame', padding="100 100")
		self.app: 'ui.gui.app.Gui' = window.app
		self.window: 'ui.gui.app.Window' = window

		self.__configure_style()

		self.logged_in = tk.BooleanVar()
		self.logged_in.set(False)


		self.submitted_switch = tk.BooleanVar()
		self.submitted_switch.set(False)

		self.username = tk.StringVar()
		self.password = tk.StringVar()

		def submit():
			self.submitted_switch.set(not self.submitted_switch.get())

		# Sign in frame
		form = ttk.Frame(self, padding="300 50", style='Secondary2.TFrame')
		form.pack(padx=25, pady=25, expand=True)

		# username
		username_label = ttk.Label(form, text="Username:")
		username_label.pack()

		self.username_entry = ttk.Entry(form, textvariable=self.username)
		self.username_entry.pack(fill='x', expand=True, pady=10)
		self.username_entry.focus()

		# password
		password_label = ttk.Label(form, text="Password:")
		password_label.pack()

		self.password_entry = ttk.Entry(form, textvariable=self.password, show="*")
		self.password_entry.pack(fill='x', expand=True, pady=10)

		# login button
		login_button = ttk.Button(form, text="Login", command=submit)
		login_button.pack(fill='x', expand=True, pady=10)


	def __configure_style(self):
		self.grid(row=0, column=0, columnspan=2,  sticky="new", padx=10, pady=150)