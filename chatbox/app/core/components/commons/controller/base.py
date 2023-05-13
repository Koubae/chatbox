import typing as t
from chatbox.app.core import tcp


class BaseController:
	def __init__(self, chat: t.Union['tcp.SocketTCPServer',  'tcp.SocketTCPClient']):
		self.chat: t.Union['tcp.SocketTCPServer',  'tcp.SocketTCPClient'] = chat
