import json
import logging
import typing as t

from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core import tcp
from chatbox.app.core.security.objects import Access
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class AuthUser:
	# Business Logic
	REQUEST_PASSWORD_AFTER_USER_CREATION: t.Final[bool] = True

	@classmethod
	def auth(cls, server: 'tcp.SocketTCPClient') -> Access:
		attempts = 0
		while server.state != objects.Client.LOGGED:
			message: str = server.receive(server.socket)
			if not message:
				raise ConnectionResetError("Server closed connection before could login")

			if _c.code_in(_c.Codes.LOGIN_SUCCESS, message):
				login_data = server.parse_json(_c.get_message(_c.Codes.LOGIN_SUCCESS, message))
				server.id = login_data["id"]
				server.login_info["id"] = server.id
				server.server_session = login_data["session_id"]
				server.state = objects.Client.LOGGED
				server._print_message(f"You are logged in, server session {server.server_session} your user id is {server.id}")
				break
			elif _c.code_in(_c.Codes.IDENTIFICATION_REQUIRED, message):
				if not server.user_id:
					server.user_id = _c.get_message(_c.Codes.IDENTIFICATION_REQUIRED, message)
					server.login_info['user_id'] = server.user_id
					_logger.info(f">>> client token is {server.user_id}")
				else:
					server._print_message("Authentication failed")
			elif _c.code_in(_c.Codes.LOGIN_CREATED, message):
				new_user_info = server.parse_json(_c.get_message(_c.Codes.LOGIN_CREATED, message))
				server.id = new_user_info["id"]
				server.user_id = new_user_info["user_id"]

				server._print_message(f"New user created {server.id}, type password again to login:")

			if attempts == 0:
				server._print_message("Identification Required")
			attempts += 1
			server.login_info['password'] = server._request_password()
			server.send(_c.make_message(_c.Codes.IDENTIFICATION, json.dumps(server.login_info)))

		return Access.GRANTED
