import json
import logging
import typing as t
from enum import Enum

from chatbox.app.constants import chat_internal_codes as codes
from .. import tcp
from ..tcp import objects
from ..model.user import UserModel, UserLoginModel
from ..security.password import generate_password_hash, check_password_hash


_logger = logging.getLogger(__name__)


class Access(Enum):
	GRANTED = True
	DENIED = False
	CREATED = -1


class AuthUser:
	# Business Logic
	REQUEST_PASSWORD_AFTER_USER_CREATION: t.Final[bool] = True

	def __new__(cls, *_, **__):
		raise NotImplementedError(f"{cls} cannot be created")

	@classmethod
	def auth(cls, server: 'tcp.SocketTCPServer', client_conn: objects.Client, payload: str) -> Access:
		logging_code_type = codes.code_in(codes.LOGIN, payload) or codes.code_in(codes.IDENTIFICATION, payload)
		logged_in = cls._login(server, logging_code_type, client_conn, payload)
		if not logged_in is Access.GRANTED:
			client_conn.login_attempts += 1
			if logged_in == Access.CREATED:
				_logger.info(f"Client {client_conn} new user created, identification required total login attempts = {client_conn.login_attempts} "
							 f"requesting identification and sending user_id")
				payload = {"id": client_conn.user.id, "user_id": client_conn.user_id}
				server.send(client_conn.connection, codes.make_message(codes.LOGIN_CREATED, json.dumps(payload)))
				return Access.CREATED

			_logger.info(f"Client {client_conn} not identified, total login attempts = {client_conn.login_attempts} "
						 f"requesting identification and sending user_id")
			server.send(client_conn.connection, codes.make_message(codes.IDENTIFICATION_REQUIRED, client_conn.user_id))
			return Access.DENIED

		payload = {"id": client_conn.user.id, "session_id": server.server_session.session_id}
		server.send(client_conn.connection, codes.make_message(codes.LOGIN_SUCCESS, json.dumps(payload)))
		return Access.GRANTED

	@classmethod
	def _login(cls, server: 'tcp.SocketTCPServer', logging_code_type: int, client_conn: objects.Client, payload: str) -> Access:
		if not logging_code_type or not client_conn or not payload:
			return Access.DENIED
		if client_conn.identifier not in server.clients_unidentified:
			return Access.DENIED
		login_info = server.parse_json(codes.get_message(logging_code_type, payload))
		if not login_info:
			return Access.DENIED

		input_user_id = login_info.get('user_id', None)
		input_user_name = login_info.get('user_name', None)
		input_user_password = login_info.get('password', None)
		_logger.info(f"{client_conn.user_name} - with user_id {client_conn.user_id} request {codes.CODES[logging_code_type]}")

		user_id_in_session = server.server_session.get_user_from_session(input_user_name)
		if not input_user_id and user_id_in_session:
			user: UserModel = server.repo_user.get(user_id_in_session)
			if user:
				cls._identify_user(server, client_conn, user, login_info, reconnected=True)
				return Access.GRANTED

		if not input_user_id or not input_user_name or not input_user_password:
			return Access.DENIED
		if input_user_id != client_conn.user_id:
			return Access.DENIED

		user: UserModel = server.repo_user.get_by_name(input_user_name)
		if not user:
			password_hash = generate_password_hash(input_user_password)
			user: UserModel = server.repo_user.create({"username": input_user_name, "password": password_hash})
			client_conn.user = user
			if cls.REQUEST_PASSWORD_AFTER_USER_CREATION:
				return Access.CREATED
		else:
			check_pass = check_password_hash(user.password, input_user_password)
			if not check_pass:
				return Access.DENIED

		cls._identify_user(server, client_conn, user, login_info, reconnected=False)
		return Access.GRANTED

	@classmethod
	def _identify_user(cls, server: 'tcp.SocketTCPServer', client_conn: objects.Client, user: UserModel, login_info: dict, reconnected: bool) -> None:
		client_conn.user_name = user.username
		client_conn.login_info = login_info
		client_conn.user = user
		client_conn.set_logged_in()

		client_conn._identifier = client_conn.identifier
		client_conn.identifier = client_conn.user.id
		server.clients_identified[client_conn.identifier] = client_conn
		del server.clients_unidentified[client_conn._identifier]

		if reconnected:
			_logger.info(f"Client {client_conn} identified with credentials {login_info} reconnected in session {server.server_session.id}")
			return

		_: UserLoginModel = server.repo_user_login.create(
			{"user_id": user.id, "session_id": server.server_session.id, "attempts": client_conn.login_attempts})

		server.server_session = server.repo_server.add_user_to_session(server.server_session, user)
		_logger.info(f"Client {client_conn} identified with credentials {login_info}")
