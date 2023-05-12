from chatbox.app.core import tcp


class BaseController:
	def __init__(self, chat: 'tcp.SocketTCPServer'):
		self.chat: 'tcp.SocketTCPServer' = chat
