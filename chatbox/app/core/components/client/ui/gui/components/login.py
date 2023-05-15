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

		self.form_send = tk.BooleanVar()
		self.form_send.set(False)


		email = tk.StringVar()
		password = tk.StringVar()

		self.email = email
		self.password = password

		def login_clicked():
			""" callback when the login button clicked
			"""
			self.form_send.set(True)

		# Sign in frame
		form = ttk.Frame(self, padding="300 50", style='Secondary2.TFrame')
		form.pack(padx=25, pady=25, expand=True)

		# email
		email_label = ttk.Label(form, text="Username:")
		email_label.pack()

		email_entry = ttk.Entry(form, textvariable=email)
		email_entry.pack(fill='x', expand=True, pady=10)
		email_entry.focus()

		# password
		password_label = ttk.Label(form, text="Password:")
		password_label.pack()

		password_entry = ttk.Entry(form, textvariable=password, show="*")
		password_entry.pack(fill='x', expand=True, pady=10)

		# login button
		login_button = ttk.Button(form, text="Login", command=login_clicked)
		login_button.pack(fill='x', expand=True, pady=10)


	def __configure_style(self):
		self.grid(row=0, column=0, columnspan=2,  sticky="new", padx=10, pady=150)