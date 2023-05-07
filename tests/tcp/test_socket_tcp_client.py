"""
How to run these test

# only this module
pytest -rP -k tcp_server
pytest -rP  tests/tcp/test_socket_tcp_server.py::TestSocketTCPServer
#  run other modules
pytest -rP -m tcp_core
pytest -rP -m tcp

"""
import threading
import time

import pytest

from chatbox.app import core

from tests.conftest import BaseRunner, UNITTEST_HOST, UNITTEST_PORT


class TestSocketTCPClient(BaseRunner):

	def _get_client_connection_from_server(self) -> core.objects.Client:
		time.sleep(.8)
		return self.tcp_server.clients_identified[list(self.tcp_server.clients_identified.keys())[0]]

	@pytest.mark.tcp_client
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_start_listening_setter_success(self, tcp_client_mock):
		client: core.SocketTCPClient = tcp_client_mock()
		sender_client = self._get_client_connection_from_server()

		assert client.connected_to_server is True
		assert sender_client.connection.getpeername() == client.socket.getsockname()

	@pytest.mark.tcp_client
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_connected_to_server_setter_fails_if_values_is_not_bool(self, tcp_client_mock):
		client: core.SocketTCPClient = tcp_client_mock()
		with pytest.raises(TypeError) as _:
			client.connected_to_server = "some values"

	@pytest.mark.tcp_client
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_request_user_name(self, tcp_client_mock, monkeypatch):
		user_mock = "userMock"
		self._request_user_name_mock = lambda : user_mock
		client: core.SocketTCPClient = tcp_client_mock(user_name=None)

		assert client.user_name == user_mock

	@pytest.mark.tcp_client
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_request_password(self, tcp_client_mock):
		password_mock = "somePassword__"
		self._request_password_mock = lambda: password_mock
		client: core.SocketTCPClient = tcp_client_mock(password=None)

		assert client.password is None

	@pytest.mark.tcp_client
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_thread_receiver(self, tcp_client_mock):
		_: core.SocketTCPClient = tcp_client_mock()
		sender_client = self._get_client_connection_from_server()
		time.sleep(.5)

		message_received = []
		self._print_message_mock = lambda message: message_received.append(message)
		message_base = "Very important message"
		message_expected = []
		total_messages = 3
		for i in range(total_messages):
			message_to_send = f"{message_base} {i}"
			message_expected.append(message_to_send)
			self.tcp_server.add_message_to_broadcast(sender_client, message_to_send, send_all=True)
			time.sleep(.5)

		assert len(message_received) == total_messages

	@pytest.mark.tcp_client
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_thread_sender(self, tcp_client_mock):
		_ = tcp_client_mock()
		_ = self._get_client_connection_from_server()
		time.sleep(.5)
		self.mock_user_input()


	# ----------------------------------
	# Auth
	# ----------------------------------
	@pytest.mark.auth_client
	@pytest.mark.auth
	@pytest.mark.tcp_client
	def test_auth_login_success(self, tcp_client_mock):
		client: core.SocketTCPClient = tcp_client_mock()
		time.sleep(1.2)

		assert client.id == self.tcp_server.clients_identified.get(client.id, None).user.id
		assert client.server_session == str(self.tcp_server.server_session.session_id)
		assert client.state == core.objects.Client.LOGGED

	@pytest.mark.auth_client
	@pytest.mark.auth
	@pytest.mark.tcp_client
	def test_exception_raised_is_server_is_unreachable(self, monkeypatch):
		tcp_client_1: core.SocketTCPClient = core.SocketTCPClient(host=UNITTEST_HOST, port=UNITTEST_PORT, user_name='user001', password='1234')

		monkeypatch.setattr(tcp_client_1, "receive", lambda *args, **kwargs: None)
		tcp_client_thread = threading.Thread(target=tcp_client_1, daemon=True)
		tcp_client_thread.start()
		time.sleep(.5)
		monkeypatch.undo()

		tcp_client_2: core.SocketTCPClient = core.SocketTCPClient(host=UNITTEST_HOST, port=UNITTEST_PORT, user_name='user001', password='1234')
		self.tcp_server.terminate()


		assert tcp_client_1.socket_connected.is_set() is False
		with pytest.raises(core.NetworkSocketException) as _:
			tcp_client_2()

		tcp_client_1.terminate()
		tcp_client_2.terminate()
