"""
How to run these test

# only this module
pytest -rP -k tcp_server
pytest -rP  tests/tcp/test_socket_tcp_server.py::TestSocketTCPServer
#  run other modules
pytest -rP -m tcp_core
pytest -rP -m tcp

"""

import pytest

from . import commons


teardown_module = commons.teardown_module
pytestmark = commons.pytestmark


class TestSocketTCPServer:

	def test_tcp_server_thread_receiver_receive_msg(self):
		for _ in range(10):
			pass

	def test_tcp_server_thread_receiver_sent_message_are_in_queue(self):
		for _ in range(10):
			pass

	def test_tcp_server_thread_receiver_stops_and_keyboard_interrupt(self):
		for _ in range(10):
			pass
			# print("Hello World")

	def test_tcp_server_broadcast_1_client(self): ...
	def test_tcp_server_broadcast_19_client(self): ...
	def test_tcp_server_broadcast_message_in_queue_consumed(self): ...