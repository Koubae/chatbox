import sys
import json
import logging
import typing as t

from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core import tcp
from chatbox.app.core.model.message import MessageModel
from chatbox.app.core.security.objects import Access
from chatbox.app.core.tcp import objects


_logger = logging.getLogger(__name__)


class AuthUser:
	# Business Logic
	REQUEST_PASSWORD_AFTER_USER_CREATION: t.Final[bool] = True

	@classmethod
	def login(cls, chat: 'tcp.SocketTCPClient') -> Access:
		attempts = 0
		while chat.state != objects.Client.LOGGED:
			message: MessageModel = chat.receive_message(chat.socket)
			if not message:
				raise ConnectionResetError("Server closed connection before could login")

			message: str = message.body
			if _c.code_in(_c.Codes.LOGIN_SUCCESS, message):
				login_data = chat.parse_json(_c.get_message(_c.Codes.LOGIN_SUCCESS, message))
				chat.id = login_data["id"]
				chat.login_info["id"] = chat.id
				chat.server_session = login_data["session_id"]
				chat.state = objects.Client.LOGGED
				chat.ui.message_echo(f"You are logged in, server session {chat.server_session} your user id is {chat.id}")
				break
			elif _c.code_in(_c.Codes.IDENTIFICATION_REQUIRED, message):
				if not chat.user_id:
					chat.user_id = _c.get_message(_c.Codes.IDENTIFICATION_REQUIRED, message)
					chat.login_info['user_id'] = chat.user_id
					_logger.info(f">>> client token is {chat.user_id}")
				else:
					chat.ui.message_echo("Authentication failed")
			elif _c.code_in(_c.Codes.LOGIN_CREATED, message):
				new_user_info = chat.parse_json(_c.get_message(_c.Codes.LOGIN_CREATED, message))
				chat.id = new_user_info["id"]
				chat.user_id = new_user_info["user_id"]

				chat.ui.message_echo(f"New user created {chat.id}, type password again to login:")

			if attempts == 0:
				chat.ui.message_echo("Identification Required")
			attempts += 1
			chat.login_info['password'] = chat.ui.input_password()

			chat.send_to_server(_c.make_message(_c.Codes.IDENTIFICATION, json.dumps(chat.login_info)))

		return Access.GRANTED

	@classmethod
	def logout(cls, chat: 'tcp.SocketTCPClient') -> None:
		chat.send_to_server(_c.make_message(_c.Codes.LOGOUT, json.dumps({"id": chat.id})))
		chat.ui.message_echo(f"Login out...")
		sys.exit(_c.Codes.LOGOUT)