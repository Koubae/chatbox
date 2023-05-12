from chatbox.app.core import tcp
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.server.auth import AuthUser
from chatbox.app.core.tcp import objects
from chatbox.app.core.tcp.objects import MessageDestination


class RouterStopRoute(Exception):
	pass


class Router:
	def __init__(self, chat: 'tcp.SocketTCPServer'):
		self.chat: 'tcp.SocketTCPServer' = chat

	def route(self, client_conn: objects.Client, payload: str) -> None:
		_route = self.route_check_client_auth(client_conn) or _c.code_scan(payload)
		match _route:
			case _c.Codes.LOGIN:
				AuthUser.auth(self.chat, client_conn, payload)
			case _c.Codes.LOGOUT:
				access = AuthUser.logout(self.chat, client_conn, payload)
				if not access.value:
					raise RouterStopRoute(f"Stop Routing, code {_c.Codes.LOGOUT}")

			case _:
				self.chat.add_message_to_broadcast(client_conn, payload, {'identifier': -1, 'destination': MessageDestination.ALL})

	@staticmethod
	def route_check_client_auth(client_conn: objects.Client) -> _c.Codes | None:
		if not client_conn.is_logged():
			return _c.Codes.LOGIN
