import os
import typing as t
from copy import deepcopy

import tkinter as tk
from tkinter import ttk

from chatbox.app.core.components.client import ui


PaneData = dict[str, list[str]]

PANE_DATA_STRUCT = {
	"users": [],
	"groups": [],
	"channels": [],
}

class ChatPane(ttk.Notebook):
	PANE_INFO = {
		"users": {
			"display_name": "Users"
		},
		"groups": {
			"display_name": "Groups"
		},
		"channels": {
			"display_name": "Channels"
		}
	}

	def __init__(self, window: 'ui.gui.app.Window', pane_data: t.Optional[PaneData] = None):
		super().__init__(window, style='TNotebook')
		self.app: 'ui.gui.app.Gui' = window.app
		self.window: 'ui.gui.app.Window' = window

		self.__configure_style()

		self._pane_data: PaneData = pane_data or deepcopy(PANE_DATA_STRUCT)

		self.pane_users = self.__build_pane_frame("users")
		self.pane_groups = self.__build_pane_frame("groups")
		self.pane_channels = self.__build_pane_frame("channels")

		self.__build_pane()

	def __configure_style(self):
		self.grid(row=0, column=0, sticky=tk.N + tk.S, padx=1, pady=1)
		self.grid_rowconfigure(0, weight=1)

	@property
	def pane_data(self) -> PaneData:
		return self._pane_data

	def add_channels(self, channels: list[str]) -> None:
		self.pane_data["channels"] = channels
		self.__build_pane_channels()


	def __build_pane_frame(self, pane_name: str) -> ttk.Frame:
		display_name = self.PANE_INFO[pane_name]["display_name"]
		frame = ttk.Frame(self.window, style='Secondary2.TFrame', padding="2 10")
		frame.grid(row=0, column=1, sticky=tk.N + tk.S, padx=10, pady=1)
		self.add(frame, text=display_name)
		return frame

	def __build_pane_users(self) -> None:
		self._build_pane_buttons(self.pane_users, self.pane_data["users"])

	def __build_pane_groups(self) -> None:
		self._build_pane_buttons(self.pane_groups, self.pane_data["groups"])

	def __build_pane_channels(self) -> None:
		self._build_pane_buttons(self.pane_channels, self.pane_data["channels"])

	def _build_pane_buttons(self, pane: ttk.Frame, items):
		for i, item in enumerate(items):
			ttk.Button(pane, text=item).grid(row=i + 2, column=0, pady=3)


	def __build_pane(self) -> None:
		"""
		data = {
			"Users": ["user1", "user2", "user3", "user4", "user5", "user6"],
			"Groups": ["group001", "group001", "group001"],
			"Channels": [f"ch{i}" for i in range(10)],
		}
		Args:
			data:

		Returns:

		"""

		self.__build_pane_users()
		self.__build_pane_groups()
		self.__build_pane_channels()
