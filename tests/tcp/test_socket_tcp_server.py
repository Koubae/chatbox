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

	def test_tcp_server(self):
		for _ in range(10):
			print("Hello World")