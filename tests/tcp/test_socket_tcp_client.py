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
import time

import pytest

from chatbox.app import core
from chatbox.app.constants import chat_internal_codes as codes

from tests.conftest import BaseRunner, TCPSocketMock, UNITTEST_HOST, UNITTEST_PORT


class TestSocketTCPClient(BaseRunner):
	@pytest.mark.tcp_client
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_start_listening_setter_success(self, tcp_client_mock):
		client: core.SocketTCPClient = tcp_client_mock()
		client.connected_to_server = True
		assert client.connected_to_server is True

	@pytest.mark.tcp_client
	@pytest.mark.tcp_core
	@pytest.mark.tcp
	def test_connected_to_server_setter_fails_if_values_is_not_bool(self, tcp_client_mock):
		client: core.SocketTCPClient = tcp_client_mock()
		with pytest.raises(TypeError) as _:
			client.connected_to_server = "some values"

	# ----------------------------------
	# Auth
	# ----------------------------------
	@pytest.mark.auth_client
	@pytest.mark.auth
	@pytest.mark.tcp_client
	def test_auth_login_success(self, tcp_client_mock):
		client: core.SocketTCPClient = tcp_client_mock()
		time.sleep(1)

		assert client.server_session == str(self.tcp_server.server_session) and client.state == core.objects.Client.LOGGED

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

