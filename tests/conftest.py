import logging
import socket
import threading
import time
import json
import typing as t

import pytest

from chatbox.app import core, constants
from chatbox.app.constants import chat_internal_codes as _c, DIR_DATABASE_SCHEMA_MAIN, SOCKET_MESSAGE_DELIMITER
from chatbox.app.core.components.server.controller.auth import ControllerAuthUser
from chatbox.app.core.security.objects import Access
from chatbox.app.database.orm.sqlite_conn import SQLITEConnection

UNITTEST_HOST: str = "127.2.9.123"
UNITTEST_PORT: int = 17219

logging.getLogger().setLevel(logging.INFO)
for _logger_name_to_disable in [
	'chatbox.app.core.tcp.network_socket',
	'chatbox.app.core.tcp.server',
	'chatbox.app.core.tcp.client',

	'chatbox.app.core.components.server.auth',

	'chatbox.app.database.sqlite_conn',
	'chatbox.app.database.repository.server_session',

]:
	_logger = logging.getLogger(_logger_name_to_disable)
	_logger.propagate = False
	_logger.disabled = True
lock = threading.Lock()
__database_mock = None


class TCPSocketMock:
	lock = threading.Lock()


	@staticmethod
	def manual_connect(_socket: socket.socket, address: tuple, socket_type: str = "tcp_server") -> bool:
		"""Manually connect the socket for unit-testing"""
		try:
			if socket_type == "tcp_server":
				_socket.bind(address)
				_socket.listen(5)
			elif socket_type == "tcp_client":
				_socket.connect(address)
			else:
				return False
		except (ConnectionRefusedError, ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError, ConnectionError) as error:
			print("Error while establishing connection to %s, reason : %s" % (address, error))
			return False
		else:

			return True

	@staticmethod
	def connect_multiple_clients(socket_factory: t.Callable[[], socket.socket], tcp_server_address: core.objects.Address, total_clients: int = 5
								 ) -> list[socket.socket]:
		clients = []
		for client in range(total_clients):
			client_socket = socket_factory()
			TCPSocketMock.manual_connect(client_socket, tcp_server_address, "tcp_client")
			clients.append(client_socket)

		return clients

	@staticmethod
	def socket_send(_socket: socket.socket, msg: str) -> None:
		_socket.send(core.NetworkSocket.encode_message(msg) + SOCKET_MESSAGE_DELIMITER)

	@staticmethod
	def socket_receive(_socket: socket.socket) -> str:
		return core.NetworkSocket.decode_message(_socket.recv(constants.SOCKET_STREAM_LENGTH))

	@staticmethod
	def login_user(tcp_server, socket_create) -> tuple[core.objects.Client, Access]:
		_sock: socket.socket = TCPSocketMock.connect_multiple_clients(socket_create, tcp_server.address, total_clients=1)[0]
		client_conn: core.objects.Client = tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		tcp_server.clients_unidentified[client_conn.identifier] = client_conn
		user_info: core.objects.LoginInfo = {
			"id": 1,
			"user_name": "user001",
			"password": "1234",
			"user_id": client_conn.user_id
		}
		login_request = _c.make_message(_c.Codes.LOGIN, json.dumps(user_info))

		controller_auth = ControllerAuthUser(tcp_server)

		login_success = controller_auth.auth(client_conn=client_conn, payload=login_request)
		return client_conn, login_success

	# ~~~~~~~~ Mocks ~~~~~~~~ #

	@staticmethod
	def mock_server_listen_once(server: socket.socket, receiver, output: dict):
		client_conn, _ = server.accept()
		with client_conn:
			data = receiver(client_conn)
			with lock:
				output["data"] = data

	@staticmethod
	def mock_server_send_once(server: socket.socket, sender, data: str):
		client_conn, _ = server.accept()
		with client_conn:
			_ = sender(client_conn, data)

	@staticmethod
	def mock_receiver(_socket: socket.socket, output: dict):
		data = None
		while not data:
			data = _socket.recv(1024)
			if data:
				with lock:
					message, _, __ = data.partition(SOCKET_MESSAGE_DELIMITER)
					output["data"] = message.decode('utf-8')
					break


# ------------------------------------------
# FIXTURES -
# ------------------------------------------
@pytest.fixture(scope="class")
def create_tcp_server_mock():
	def set_up() -> core.SocketTCPServer:
		print("FIXTURE: create_tcp_server_mock -> set_up")

		ControllerAuthUser.REQUEST_PASSWORD_AFTER_USER_CREATION = False  # Skip The

		core.SocketTCPServer._connect_to_database = lambda _: __database_mock

		tcp_server: core.SocketTCPServer = core.SocketTCPServer(UNITTEST_HOST, UNITTEST_PORT)

		tcp_server_thread = threading.Thread(target=tcp_server, daemon=True)
		tcp_server_thread.start()

		return tcp_server

	def tear_down(tcp_server: core.SocketTCPServer):
		print("FIXTURE: create_tcp_server_mock -> tear_down")
		tcp_server.terminate()

	server = set_up()
	yield server

	tear_down(server)


@pytest.fixture(scope="function")
def tcp_client_mock() -> t.Callable[..., core.SocketTCPClient]:
	clients: list[core.SocketTCPClient] = []
	def set_up(host = UNITTEST_HOST, port = UNITTEST_PORT, user_name = 'user001', password = '1234'):
		tcp_client: core.SocketTCPClient = core.SocketTCPClient(host=host, port=port, user_name=user_name, password=password)
		tcp_client_thread = threading.Thread(target=tcp_client, daemon=True)
		tcp_client_thread.start()

		clients.append(tcp_client)
		return tcp_client

	yield set_up

	for client in clients:
		client.terminate()


@pytest.fixture(scope='function')
def network_socket(request) -> core.NetworkSocket:
	param = hasattr(request, "param") and request.param or {'host': UNITTEST_HOST, 'port': UNITTEST_PORT}
	network_socket = core.NetworkSocket(**param)

	yield network_socket

	network_socket.terminate()


@pytest.fixture(scope='function')
def _socket() -> socket.socket:
	socket_options = [(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)]
	_socket = core.NetworkSocket.create_tcp_socket(socket_options)

	yield _socket

	_socket.close()


@pytest.fixture(scope='function')
def socket_create() -> t.Callable[[], socket.socket]:
	sockets: list[socket.socket] = []

	def _make():
		socket_options = [(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)]
		_socket = core.NetworkSocket.create_tcp_socket(socket_options)
		sockets.append(_socket)
		return _socket

	yield _make

	for _sock in sockets:
		_sock.close()


@pytest.fixture(scope="class")
def create_database_mock():
	global __database_mock
	print("FIXTURE: create_database_mock -> set_up")
	database: SQLITEConnection = SQLITEConnection(":memory:", schema=DIR_DATABASE_SCHEMA_MAIN)
	database.cursor.execute("PRAGMA foreign_keys = OFF;")
	__database_mock = database

	yield database

	print("FIXTURE: create_database_mock -> tear_down")
	del database


class BaseRunner:
	"""Base Runner where all unit-tests should inherit from"""

	event_input = threading.Event()

	@pytest.fixture(autouse=True)
	def _app(self, create_database_mock, create_tcp_server_mock, monkeypatch):
		monkeypatch.setattr(core.client_components.ui.Terminal, "message_echo", lambda _self, message: self._print_message_mock(message))
		monkeypatch.setattr(core.client_components.ui.Terminal, "message_prompt", lambda _self: self._request_message_mock())
		monkeypatch.setattr(core.client_components.ui.Terminal, "input_username", lambda _self: self._request_user_name_mock())
		monkeypatch.setattr(core.client_components.ui.Terminal, "input_password", lambda _self: self._request_password_mock())

		self.db: SQLITEConnection = create_database_mock
		self.tcp_server: core.SocketTCPServer = create_tcp_server_mock


	@pytest.fixture(scope="function", autouse=True)
	def tear_down_db(self):
		with lock:
			with self.db.connection:
				cursor = self.db.connection.cursor()
				cursor.execute("DELETE FROM user_login")
				cursor.execute("DELETE FROM user")
				cursor.execute("DELETE FROM server_session")

	def _print_message_mock(self, message: str) -> None:
		pass

	def _request_message_mock(self) -> str:
		self.event_input.wait()
		return "some input"

	def _request_user_name_mock(self) -> str:
		return "user001"

	def _request_password_mock(self) -> str:
		return "1234"

	def mock_user_input(self, _: str = "some input"):
		self.event_input.set()
		time.sleep(.3)
		self.event_input.clear()