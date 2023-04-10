import logging
import socket
import threading

import pytest

from chatbox.app.core.tcp.network_socket import NetworkSocket


for _logger_name_to_disable in [
	'chatbox.app.core.tcp.network_socket',
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

	@staticmethod
	def mock_socket_send(_socket: socket.socket, msg: str):
		_socket.send(msg.encode('utf-8'))


# ------------------------------------------
# FIXTURES -
# ------------------------------------------


@pytest.fixture(scope='function')
def create_socket(request) -> NetworkSocket:
	param = hasattr(request, "param") and request.param or {'host': 'localhost', 'port': 10_000}
	network_socket = NetworkSocket(**param)

	yield network_socket

	network_socket.terminate()
