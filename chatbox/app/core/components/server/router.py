from chatbox.app.core import tcp
from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core.components.server.controller.auth import ControllerAuthUser
from chatbox.app.core.components.server.controller.send_message import ControllerSendTo
from chatbox.app.core.model.message import MessageRole, MessageDestination, ServerMessageModel
from chatbox.app.core.tcp import objects


class RouterStopRoute(Exception):
	pass


class Router:
	def __init__(self, chat: 'tcp.SocketTCPServer'):
		self.chat: 'tcp.SocketTCPServer' = chat

		self.controller_auth: ControllerAuthUser = ControllerAuthUser(self.chat)
		self.controller_send_to: ControllerSendTo = ControllerSendTo(self.chat)

	def route(self, client_conn: objects.Client, payload: ServerMessageModel) -> None:
		_route = self.route_check_client_auth(client_conn) or _c.code_scan(payload.body)
		match _route:
			case _c.Codes.LOGIN:
				self.controller_auth.auth(client_conn, payload.body)
			case _c.Codes.LOGOUT:
				access = self.controller_auth.logout(client_conn, payload.body)
				if not access.value:
					raise RouterStopRoute(f"Stop Routing, code {_c.Codes.LOGOUT}")

			case _c.Codes.SEND_TO_ALL:
				self.controller_send_to.all(client_conn, payload)
			case _:
				self.controller_send_to.all(client_conn, payload)

	@staticmethod
	def route_check_client_auth(client_conn: objects.Client) -> _c.Codes | None:
		if not client_conn.is_logged():
			return _c.Codes.LOGIN
