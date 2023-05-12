from chatbox.app.core import tcp
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.server.auth import AuthUser
from chatbox.app.core.tcp import objects


class RouterStopRoute(Exception):
	pass


class Router:
	def __init__(self, chat: 'tcp.SocketTCPServer'):
		self.chat: 'tcp.SocketTCPServer' = chat

	def route(self, client_conn: objects.Client, payload: str) -> None:
		# TODO: move LOGIN inside this logic?
		_route = _c.code_scan(payload)
		match _route:
			case _c.Codes.LOGOUT:
				access = AuthUser.logout(self.chat, client_conn, payload)
				if not access.value:
					raise RouterStopRoute(f"Stop Routing, code {_c.Codes.LOGOUT}")

			case _:
				self.chat.add_message_to_broadcast(client_conn, payload)
