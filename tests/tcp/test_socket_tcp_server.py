"""
How to run these test

# only this module
pytest -rP -k tcp_server
pytest -rP  tests/tcp/test_socket_tcp_server.py::TestSocketTCPServer
#  run other modules
pytest -rP -m tcp_core
pytest -rP -m tcp

"""
import socket
import threading

import pytest

from chatbox.app import core
from chatbox.app.constants import chat_internal_codes as codes

from tests.conftest import BaseRunner, TCPSocketMock, UNITTEST_HOST, UNITTEST_PORT


class TestSocketTCPServer(BaseRunner):
	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_accept_new_connection(self, socket_create):
		to_delete = set()
		for identifier, client in self.tcp_server.clients_undentified.items():
			client.connection.close()
			to_delete.add(identifier)
		for _identifier in to_delete:
			del self.tcp_server.clients_undentified[_identifier]

		sockets: list[socket.socket] = TCPSocketMock.connect_multiple_clients(socket_create, self.tcp_server.address)
		for _sock in sockets:
			TCPSocketMock.socket_send(_sock, "ping")
		_ = [TCPSocketMock.socket_receive(_sock) for _sock in sockets]

		results = []
		for _sock in sockets:
			for identifier, client in self.tcp_server.clients_undentified.items():
				if client.connection.getpeername() == _sock.getsockname():
					results.append(client.address == core.objects.Address(*_sock.getsockname()))
					break
			else:
				results.append(False)

		assert len(sockets) == len(self.tcp_server.clients_undentified) and all(results)

	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_tcp_server_thread_receiver_receive_msg(self, socket_create):
		sockets: list[socket.socket] = TCPSocketMock.connect_multiple_clients(socket_create, self.tcp_server.address)
		for _sock in sockets:
			TCPSocketMock.socket_send(_sock, "ping")

		messages = [TCPSocketMock.socket_receive(_sock) for _sock in sockets]
		messages_unique = set(messages)
		check_message_contains_code = [codes.code_in(codes.IDENTIFICATION_REQUIRED, payload) for payload in messages]
		check_message_contains_code_expected = [codes.IDENTIFICATION_REQUIRED for _ in messages]

		assert check_message_contains_code == check_message_contains_code_expected
		assert len(messages) == len(messages_unique)

	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_tcp_server_thread_receiver_sent_message_are_in_queue(self, socket_create):
		total_clients = 5
		sockets: list[socket.socket] = TCPSocketMock.connect_multiple_clients(socket_create, self.tcp_server.address, total_clients=total_clients)
		for _sock in sockets:
			TCPSocketMock.socket_send(_sock, "ping")
		_ = [TCPSocketMock.socket_receive(_sock) for _sock in sockets]
		sender_client = self.tcp_server.clients_undentified[list(self.tcp_server.clients_undentified.keys())[0]]
		total_messages = 10
		for i in range(total_messages):
			message = f"message_{i}"
			self.tcp_server.add_message_to_broadcast(sender_client, message, send_all=True)

		messages = []
		def receive_thread(_socket_to_listen):
			msg = TCPSocketMock.socket_receive(_socket_to_listen)
			messages.append(msg)

		threads = [threading.Thread(target=receive_thread, args=(_sock, ), daemon=True)
			for index, _sock in enumerate(sockets)
				if sender_client.connection.getpeername() != _sock.getsockname()
		]

		for t in threads:
			t.start()
		for t in threads:
			t.join(timeout=.5)

		result = []
		for message in messages:
			for message_count in range(total_messages):
				message_expected = f"message_{message_count}"
				result.append(message_expected in message)

		assert len(messages) == total_clients - 1 and all(result) and self.tcp_server.client_messages.qsize() == 0

	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_create_client_identifier(self, socket_create):
		client_socket: socket.socket = socket_create()
		client_identifier = core.SocketTCPServer.create_client_identifier(client_socket, core.objects.Address(UNITTEST_HOST, UNITTEST_PORT))

		assert ('id' in client_identifier and isinstance(client_identifier['id'], int)) and \
			   ('identifier' in client_identifier and isinstance(client_identifier['identifier'], int))
