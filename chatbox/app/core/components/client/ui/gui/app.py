import os

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # new widget ui
from tkinter import scrolledtext
from chatbox import __version__
from chatbox.app.core.components.client.ui.gui.components.menu import MenuMain

try:
	# windows text blur
	from ctypes import windll
	windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
	pass


from chatbox.app.constants import DIR_GUI_ASSETS, APP_NAME_CLIENT

DEFAULT_1 = "#0c0d0d"
DEFAULT_2 = "#bec4c4"

DANGER = "#b8000f"
DANGER_LIGHT = "#ffabb2"

COLOR_PRIMARY = "#07e6b4" 
COLOR_PRIMARY_9 = "#009a73"
COLOR_PRIMARY_10 = "#027054"

COLOR_SECONDARY = "#25217b"
COLOR_SECONDARY_9 = "#050317"


class Window(ttk.Frame):
	def __init__(self, master: 'App'):
		super().__init__()
		self.app: 'App' = master

		# create a new style
		self.style = ttk.Style()
		self.style.theme_use("default")
		# configure it to the background you want
		self.style.configure('Main.TFrame', background=COLOR_SECONDARY_9, foreground="white")
		self.style.configure('Chat.TFrame', background=COLOR_SECONDARY_9, foreground="white")
		self.style.configure('Secondary.TFrame', background=COLOR_SECONDARY_9)
		self.style.configure('Secondary2.TFrame', background=COLOR_SECONDARY)
		self.style.configure('Primary.TFrame', background=COLOR_PRIMARY)
		self.style.configure('Default2.TFrame', background=DEFAULT_1)

		self.style.configure('TButton', background=COLOR_PRIMARY, foreground='white', width=20, borderwidth=3, focusthickness=3, focuscolor='none')
		self.style.map('TButton', background=[('active', COLOR_PRIMARY_9), ('pressed', COLOR_PRIMARY_10)])
		self.style.map("Danger.TButton",
				  background=[("active", DANGER), ("!active", DANGER_LIGHT)],
				  foreground=[("active", "white"), ("!active", "black")])
		self.style.map("Secondary.TButton",
					   background=[("active", COLOR_SECONDARY_9), ("!active", COLOR_SECONDARY)],
					   foreground=[("active", "white"), ("!active", "white")])

		self.style.configure(".", font=('Helvetica', 12), foreground="white")
		self.style.configure("Treeview", background=COLOR_SECONDARY_9, foreground='white')
		self.style.configure("Treeview.Heading", background=COLOR_PRIMARY_9, foreground='white')



		self.config(style='Main.TFrame')
		self.grid(column=0, row=0, sticky=tk.N + tk.W + tk.E + tk.S)

		self.grid_columnconfigure(2, weight=2)
		self.grid_rowconfigure(0, weight=1)

		self.menu: MenuMain = MenuMain(self)

		# ----------------------
		# CHAT TYPES
		# ----------------------

		self.chat_types = ttk.Frame(self, style='Secondary.TFrame', padding="15 10")
		self.chat_types.grid(row=0, column=0, sticky=tk.N + tk.S, padx=1, pady=1)

		ttk.Button(self.chat_types, text="Channels", style='Secondary.TButton', width=10).grid(row=2, column=0, pady=10, sticky=tk.W)
		ttk.Button(self.chat_types, text="Groups", style='Secondary.TButton', width=10).grid(row=3, column=0, pady=10, sticky=tk.W)
		ttk.Button(self.chat_types, text="Users", style='Secondary.TButton', width=10).grid(row=4, column=0, pady=10, sticky=tk.W)

		self.chat_types.grid_rowconfigure(0, weight=0)
		self.chat_types.grid_rowconfigure(1, weight=2)

		self.chat_types.grid_rowconfigure(2, weight=0)
		self.chat_types.grid_rowconfigure(3, weight=0)
		self.chat_types.grid_rowconfigure(4, weight=0)

		self.chat_types.grid_rowconfigure(5, weight=4)

		# ----------------------
		# CHAT STACK
		# ----------------------

		self.chat_stack = ttk.Frame(self, style='Secondary2.TFrame', padding="2 10")
		self.chat_stack.grid(row=0, column=1, sticky=tk.N + tk.S, padx=10, pady=1)

		for i in range(2, 3+2):
			ttk.Button(self.chat_stack, text=f"Button {i}").grid(row=i+2, column=0, pady=3)

		self.chat_stack.grid_rowconfigure(0, weight=0)
		self.chat_stack.grid_rowconfigure(1, weight=1)

		# ----------------------
		# CHAT
		# ----------------------

		self.chat = ttk.Frame(self, style='Chat.TFrame')
		self.chat.grid(row=0, column=2, sticky="nsew", padx=1, pady=1)

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
		tree.configure(yscroll=scrollbar.set)
		scrollbar.grid(row=0, column=2, rowspan=2, sticky=tk.N + tk.S)

		self.message_container = ttk.Frame(self.chat, style="Secondary2.TFrame")
		self.message_container.grid(row=2, column=0, columnspan=3, pady=0, sticky=tk.E + tk.W + tk.N + tk.S)
		self.message_container.rowconfigure(0, weight=1)
		self.message_container.columnconfigure(0, weight=1)

		self.message_text = scrolledtext.ScrolledText(self.message_container, width=40, height=5, font=('Times New Roman', 14, 'italic'),
													  background=COLOR_SECONDARY_9, foreground="white")
		# self.message_text_entry = Entry(self.message_container, width=40,  font=('Times New Roman', 14, 'italic'), background=COLOR_SECONDARY_9, foreground="white")
		self.message_text.focus()
		self.message_text.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

		self.button_message_submit = ttk.Button(self.message_container, width=10, text="Send", command=lambda: self.message_submit())
		self.button_message_submit.grid(column=1, rows=1)

		self.button_message_clear = ttk.Button(self.message_container, width=10, text="Clear", style='Danger.TButton', command=lambda: self.message_clear())
		self.button_message_clear.grid(column=1, rows=1)

		message_chat_type = "scroll"
		if message_chat_type == "entry":
			self.message_text.bind("<Return>", lambda _: self.message_submit())

	def message_submit(self, _type = "scroll") -> str:
		if _type == "entry":
			message = self.message_text.get()  # noqa
		else:
			message = self.message_text.get("1.0", tk.END)
		if "\n" == message[0]: # Remove first char if is empty space
			message = message[1:]
		message_removed_last_char = message
		print(message_removed_last_char)
		self.message_clear()
		return message_removed_last_char

	def message_clear(self, _type = "scroll") -> None:
		if _type == "entry":
			self.message_text.delete('0', tk.END)
		else:
			self.message_text.delete('1.0', tk.END)

	def on_close_app(self):
		response = messagebox._show(  # noqa
			"Warning",
			f"You are about to close {APP_NAME_CLIENT}, are you sure?",
			messagebox.WARNING,
			messagebox.YESNOCANCEL,
		)
		if response == "yes":
			self.master.destroy()


class App(tk.Tk):
	def __init__(self):
		super().__init__()

		self.state = False
		self.window_width = self.winfo_screenwidth()
		self.window_height = self.winfo_screenheight()

		self.__configure_app()
		self.__register_events()

		self.window: Window = Window(self)

	def __call__(self) -> None:
		self.mainloop()

	def action_full_screen(self, _=None):
		self.state = not self.state
		self.attributes("-fullscreen", self.state)

	def action_full_screen_out(self, _=None):
		self.state = False
		self.attributes("-fullscreen", False)

	def __configure_app(self):
		self.title(f'{APP_NAME_CLIENT} - v{__version__.__version__} {__version__.__build__}')

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self.attributes('-zoomed', True)
		self.attributes('-topmost', 1)

		self.configure(background=COLOR_PRIMARY_9)
		self.option_add('*Dialog.msg.width', 150)
		self.option_add('*Dialog.msg.height', 80)
		self.option_add("*Dialog.msg.wrapLength", "18i")

	def __register_events(self):
		self.bind("<F11>", self.action_full_screen)
		self.bind("<Escape>", self.action_full_screen_out)


if __name__ == '__main__':
	app = App()
	app()