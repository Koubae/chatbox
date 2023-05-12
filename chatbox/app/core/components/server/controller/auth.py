import json
import logging
import typing as t

from chatbox.app.constants import chat_internal_codes as _c
from chatbox.app.core import tcp
from chatbox.app.core.security.objects import Access
from chatbox.app.core.tcp import objects
from chatbox.app.core.model.user import UserModel, UserLoginModel
from chatbox.app.core.security.password import generate_password_hash, check_password_hash


_logger = logging.getLogger(__name__)


class ControllerAuthUser:
	REQUEST_PASSWORD_AFTER_USER_CREATION: t.Final[bool] = True

	def __init__(self, chat: 'tcp.SocketTCPServer'):
		self.chat: 'tcp.SocketTCPServer' = chat

	def auth(self, client_conn: objects.Client, payload: str) -> Access:
		logging_code_type = _c.code_in(_c.Codes.LOGIN, payload) or _c.code_in(_c.Codes.IDENTIFICATION, payload)
		logged_in = self._login(logging_code_type, client_conn, payload)
		if not logged_in is Access.GRANTED:
			client_conn.login_attempts += 1
			if logged_in == Access.CREATED:
				_logger.info(f"Client {client_conn} new user created, identification required total login attempts = {client_conn.login_attempts} "
							 f"requesting identification and sending user_id")
				payload = {"id": client_conn.user.id, "user_id": client_conn.user_id}

				self.chat.send_to_client(client_conn, _c.make_message(_c.Codes.LOGIN_CREATED, json.dumps(payload)))
				return Access.CREATED

			_logger.info(f"Client {client_conn} not identified, total login attempts = {client_conn.login_attempts} "
						 f"requesting identification and sending user_id")

			self.chat.send_to_client(client_conn, _c.make_message(_c.Codes.IDENTIFICATION_REQUIRED, client_conn.user_id))
			return Access.DENIED

		payload = {"id": client_conn.user.id, "session_id": self.chat.server_session.session_id}
		self.chat.send_to_client(client_conn,_c.make_message(_c.Codes.LOGIN_SUCCESS, json.dumps(payload)))
		return Access.GRANTED

	def logout(self, client_conn: objects.Client, payload: str) -> Access:
		user_id = self.chat.parse_json(_c.get_message(_c.Codes.LOGOUT, payload))
		self.chat.send_to_client(client_conn, _c.make_message(_c.Codes.LOGOUT, f"User {user_id} logged out!"))

		self.chat.server_session = self.chat.repo_server.remove_user_to_session(self.chat.server_session, client_conn.user)
		_logger.info(f"Client {client_conn.user} removed from session")
		return Access.DENIED

	def _login(self, logging_code_type: _c.Codes | None, client_conn: objects.Client, payload: str) -> Access:
		if not logging_code_type or not client_conn or not payload:
			return Access.DENIED
		if client_conn.identifier not in self.chat.clients_unidentified:
			return Access.DENIED
		login_info = self.chat.parse_json(_c.get_message(logging_code_type, payload))
		if not login_info:
			return Access.DENIED

		input_user_id = login_info.get('user_id', None)
		input_user_name = login_info.get('user_name', None)
		input_user_password = login_info.get('password', None)
		_logger.info(f"{client_conn.user_name} - with user_id {client_conn.user_id} request {logging_code_type}")

		user_id_in_session = self.chat.server_session.get_user_from_session(input_user_name)
		if not input_user_id and user_id_in_session:
			user: UserModel = self.chat.repo_user.get(user_id_in_session)
			if user:
				self._identify_user(client_conn, user, login_info, reconnected=True)
				return Access.GRANTED

		if not input_user_id or not input_user_name or not input_user_password:
			return Access.DENIED
		if input_user_id != client_conn.user_id:
			return Access.DENIED

		user: UserModel = self.chat.repo_user.get_by_name(input_user_name)
		if not user:
			password_hash = generate_password_hash(input_user_password)
			user: UserModel = self.chat.repo_user.create({"username": input_user_name, "password": password_hash})
			client_conn.user = user
			if self.REQUEST_PASSWORD_AFTER_USER_CREATION:
				return Access.CREATED
		else:
			check_pass = check_password_hash(user.password, input_user_password)
			if not check_pass:
				return Access.DENIED

		self._identify_user( client_conn, user, login_info, reconnected=False)
		return Access.GRANTED

	def _identify_user(self, client_conn: objects.Client, user: UserModel, login_info: dict, reconnected: bool) -> None:
		client_conn.user_name = user.username
		client_conn.login_info = login_info
		client_conn.user = user
		client_conn.set_logged_in()

		client_conn._identifier = client_conn.identifier
		client_conn.identifier = client_conn.user.id
		self.chat.clients_identified[client_conn.identifier] = client_conn
		del self.chat.clients_unidentified[client_conn._identifier]

		if reconnected:
			_logger.info(f"Client {client_conn} identified with credentials {login_info} reconnected in session {self.chat.server_session.id}")
			return

		_: UserLoginModel = self.chat.repo_user_login.create(
			{"user_id": user.id, "session_id": self.chat.server_session.id, "attempts": client_conn.login_attempts})

		self.chat.server_session = self.chat.repo_server.add_user_to_session(self.chat.server_session, user)
		_logger.info(f"Client {client_conn} identified with credentials {login_info}")
