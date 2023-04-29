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
import json
import threading

import pytest

from chatbox.app import core
from chatbox.app.constants import chat_internal_codes as codes

from tests.conftest import BaseRunner, TCPSocketMock, UNITTEST_HOST, UNITTEST_PORT


class TestSocketTCPServer(BaseRunner):
	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_start_listening_setter_success(self):
		self.tcp_server.server_listening = True
		assert self.tcp_server.server_listening is True

	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_start_listening_setter_fails_if_values_is_not_bool(self):
		with pytest.raises(TypeError) as _:
			self.tcp_server.server_listening = "some values"

	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_start_listening_getter(self):
		assert self.tcp_server.server_listening is True


	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_accept_new_connection(self, socket_create):
		sockets: list[socket.socket] = TCPSocketMock.connect_multiple_clients(socket_create, self.tcp_server.address)
		for _sock in sockets:
			TCPSocketMock.socket_send(_sock, "ping")
		_ = [TCPSocketMock.socket_receive(_sock) for _sock in sockets]

		results = []
		for _sock in sockets:
			for identifier, client in self.tcp_server.clients_unidentified.items():
				if client.connection.getpeername() == _sock.getsockname():
					results.append(client.address == core.objects.Address(*_sock.getsockname()))
					break
			else:
				results.append(False)

		assert len(sockets) == len(self.tcp_server.clients_unidentified) and all(results)

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
		sender_client = self.tcp_server.clients_unidentified[list(self.tcp_server.clients_unidentified.keys())[0]]
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

	# ----------------------------------
	# Auth
	# ----------------------------------
	@pytest.mark.auth_server
	@pytest.mark.auth
	@pytest.mark.tcp_server
	def test_auth_login_returns_false_if_user_not_in_clients_undentified(self, socket_create):
		_sock = socket_create()
		client_conn: core.objects.Client = self.tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		user_info: core.objects.LoginInfo = {
			"user_name": "user001",
			"password": "1234",
			"user_id": client_conn.user_id
		}

		assert self.tcp_server.login(logging_code_type=codes.LOGIN, client_conn=client_conn, payload=json.dumps(user_info)) is False

	@pytest.mark.auth_server
	@pytest.mark.auth
	@pytest.mark.tcp_server
	def test_auth_login_returns_false_if_provided_items_are_falsy(self, socket_create):
		_sock = socket_create()
		client_conn: core.objects.Client = self.tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		self.tcp_server.clients_unidentified[client_conn.identifier] = client_conn

		assert self.tcp_server.login(logging_code_type=None, client_conn=client_conn, payload='{"payload": 123}') is False  # noqa
		assert self.tcp_server.login(logging_code_type=123, client_conn=None, payload='{"payload": 123}') is False  # noqa
		assert self.tcp_server.login(logging_code_type=123, client_conn=client_conn, payload='') is False  # noqa

	@pytest.mark.auth_server
	@pytest.mark.auth
	@pytest.mark.tcp_server
	def test_auth_login_returns_false_if_payload_is_not_json(self, socket_create):
		_sock = socket_create()
		client_conn: core.objects.Client = self.tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		self.tcp_server.clients_unidentified[client_conn.identifier] = client_conn

		assert self.tcp_server.login(logging_code_type=codes.LOGIN, client_conn=client_conn, payload='{"values": "itme""somethingwrong"}') is False  # noqa

	@pytest.mark.auth_server
	@pytest.mark.auth
	@pytest.mark.tcp_server
	def test_auth_login_success(self, socket_create):
		_sock = socket_create()
		client_conn: core.objects.Client = self.tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		self.tcp_server.clients_unidentified[client_conn.identifier] = client_conn
		user_info: core.objects.LoginInfo = {
			"user_name": "user001",
			"password": "1234",
			"user_id": client_conn.user_id
		}

		assert self.tcp_server.login(logging_code_type=codes.LOGIN, client_conn=client_conn, payload=json.dumps(user_info)) is True and \
			client_conn.is_logged() and client_conn.identifier not in self.tcp_server.clients_unidentified

	@pytest.mark.auth_server
	@pytest.mark.auth
	@pytest.mark.tcp_server
	def test_auth_login_false_if_user_id_not_match(self, socket_create):
		_sock = socket_create()
		client_conn: core.objects.Client = self.tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		self.tcp_server.clients_unidentified[client_conn.identifier] = client_conn
		user_info: core.objects.LoginInfo = {
			"user_name": "user001",
			"password": "1234",
			"user_id": "nope"
		}

		assert self.tcp_server.login(logging_code_type=codes.LOGIN, client_conn=client_conn, payload=json.dumps(user_info)) is False

	@pytest.mark.auth_server
	@pytest.mark.auth
	@pytest.mark.tcp_server
	def test_auth_login_false_if_user_name_not_exists(self, socket_create):
		_sock = socket_create()
		client_conn: core.objects.Client = self.tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		self.tcp_server.clients_unidentified[client_conn.identifier] = client_conn
		user_info: core.objects.LoginInfo = {
			"user_name": None,
			"password": "1234",
			"user_id": client_conn.user_id
		}

		assert self.tcp_server.login(logging_code_type=codes.LOGIN, client_conn=client_conn, payload=json.dumps(user_info)) is False


	@pytest.mark.auth_server
	@pytest.mark.auth
	@pytest.mark.tcp_server
	def test_auth_login_request_success(self, socket_create):
		_sock: socket.socket = TCPSocketMock.connect_multiple_clients(socket_create, self.tcp_server.address, total_clients=1)[0]
		client_conn: core.objects.Client = self.tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		self.tcp_server.clients_unidentified[client_conn.identifier] = client_conn
		user_info: core.objects.LoginInfo = {
			"user_name": "user001",
			"password": "1234",
			"user_id": client_conn.user_id
		}
		login_request = codes.make_message(codes.LOGIN, json.dumps(user_info))

		assert self.tcp_server.login_request(client_conn=client_conn, payload=login_request) is True


	@pytest.mark.auth_server
	@pytest.mark.auth
	@pytest.mark.tcp_server
	def test_auth_login_request_failed_response_must_contain_code_identification_required(self, socket_create):
		_sock: socket.socket = TCPSocketMock.connect_multiple_clients(socket_create, self.tcp_server.address, total_clients=1)[0]
		client_conn: core.objects.Client = self.tcp_server.create_client_object(_sock, core.objects.Address(*_sock.getsockname()))
		self.tcp_server.clients_unidentified[client_conn.identifier] = client_conn
		user_info: core.objects.LoginInfo = {
			"user_name": "user001",
			"password": "1234",
			"user_id": "nope"
		}
		login_request = codes.make_message(codes.LOGIN, json.dumps(user_info))

		self.tcp_server.login_request(client_conn=client_conn, payload=login_request)

		messages = []
		def receive_thread(_socket_to_listen):
			msg = TCPSocketMock.socket_receive(_socket_to_listen)
			messages.append(msg)

		t = threading.Thread(target=receive_thread, args=(_sock,), daemon=True)
		t.start()
		t.join(timeout=.5)

		assert codes.code_in(codes.IDENTIFICATION_REQUIRED, messages[0]) is codes.IDENTIFICATION_REQUIRED

	@pytest.mark.tcp_server
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_stop_listening_stop_accepting_new_connections(self, socket_create):
		sockets: list[socket.socket] = TCPSocketMock.connect_multiple_clients(socket_create, self.tcp_server.address)
		for _sock in sockets:
			TCPSocketMock.socket_send(_sock, "ping")

		self.tcp_server.stop_listening()

		sockets = TCPSocketMock.connect_multiple_clients(socket_create, self.tcp_server.address, total_clients=2)
		socket_after_server_stopped_listen = sockets[1]

		with pytest.raises(OSError) as _:
			TCPSocketMock.socket_receive(socket_after_server_stopped_listen)
		assert self.tcp_server.server_listening is False
