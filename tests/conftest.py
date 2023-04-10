import logging
import socket
import threading
import typing as t

import pytest

from chatbox.app import core
from chatbox.app import constants

UNITTEST_HOST: str = "127.2.9.123"
UNITTEST_PORT: int = 17219
for _logger_name_to_disable in [
	'chatbox.app.core.tcp.network_socket',
	# 'chatbox.app.core.tcp.server',
]:
	_logger = logging.getLogger(_logger_name_to_disable)
	_logger.propagate = False
	_logger.disabled = True
lock = threading.Lock()


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
		_socket.send(core.NetworkSocket.encode_message(msg))

	@staticmethod
	def socket_receive(_socket: socket.socket) -> str:
		return core.NetworkSocket.decode_message(_socket.recv(constants.SOCKET_STREAM_LENGTH))

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
					output["data"] = data.decode('utf-8')
					break


# ------------------------------------------
# FIXTURES -
# ------------------------------------------
@pytest.fixture(scope="session")
def create_tcp_server_mock():
	def set_up():
		print("FIXTURE: create_tcp_server_mock -> set_up")
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

class BaseRunner:
	"""Base Runner where all unit-tests should inherit from"""

	@pytest.fixture(autouse=True)
	def _app(self, create_tcp_server_mock):
		self.tcp_server: core.SocketTCPServer = create_tcp_server_mock

