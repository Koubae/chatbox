"""
How to run these test

# only this module
pytest -rP -k net_socket
pytest -rP  tests/tcp/test_network_socket.py::TestNetworkSocket
#  run other modules
pytest -rP -m tcp_core
pytest -rP -m tcp

"""

import socket
import pytest
import threading
import time
from chatbox.app.core.tcp.network_socket import NetworkSocket
from chatbox.app import constants

from . import commons


teardown_module = commons.teardown_module
pytestmark = commons.pytestmark

class TestNetworkSocket:

    def test_net_socket_instance_constructor(self):
        network_socket: NetworkSocket = commons.create_socket("localhost", 10_000)
        assert type(network_socket.socket) is socket.socket

    def test_net_socket_get_app_host_get_default(self):
        my_host = constants.SOCKET_HOST_DEFAULT
        expected = socket.gethostbyname(socket.gethostname())

        app_host = NetworkSocket.get_app_host(my_host)

        assert  app_host == expected

    def test_net_socket_get_app_host_custom(self):
        my_host = "199.123.180.20"

        app_host = NetworkSocket.get_app_host(my_host)

        assert my_host == app_host

    def test_net_socket_create_tcp_socket(self):
        socket_options = [(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)]

        _socket = NetworkSocket.create_tcp_socket(socket_options)

        assert type(_socket) is socket.socket
        assert isinstance(_socket, socket.socket)
        assert isinstance(_socket, socket.socket)

    def test_net_socket_socket_connect_returns_false_because_is_abstract(self):
        network_socket: NetworkSocket = commons.create_socket("localhost", 10_000)
        connected: bool = network_socket.socket_connect()
        assert connected is False

    def test_net_socket_run_network_socket_raise_because_is_abstract(self):
        network_socket: NetworkSocket = commons.create_socket("localhost", 10_000)
        with pytest.raises(Exception) as _:
            network_socket()

    def test_net_socket_wait_or_die(self):
        seconds_to_wait = 3   # wait outside of the wait_or_die
        seconds_to_trigger_close = 2  # when we reach this amount, will manually 'close' the NetworkSocket so that wait_or_die must stop and call close to self

        network_socket: NetworkSocket = commons.create_socket("localhost", 10_000)
        network_socket.socket_connected = True # mock that the server is connected

        waiting_thread = threading.Thread(target=network_socket.start_wait_forever, daemon=True) # let's put it in a thread in order to monitor it
        waiting_thread.start()

        while seconds_to_wait:
            time.sleep(1)
            seconds_to_wait -= 1
            if seconds_to_trigger_close == seconds_to_wait:
                network_socket.stop_wait_forever()

        assert network_socket.socket_connected is False

    def test_net_socket_overridable_functions_must_return_notImplemented(self):
        network_socket: NetworkSocket = commons.create_socket("localhost", 10_000)

        assert network_socket.socket_on_before() is NotImplemented
        assert network_socket.socket_on_after(network_socket.socket) is NotImplemented
        assert network_socket.start_before() is NotImplemented
        assert network_socket.start_after() is NotImplemented
        assert network_socket.start() is NotImplemented
        assert network_socket.close_before() is NotImplemented
        assert network_socket.close_after() is NotImplemented

    def test_net_socket_overridable_functions_raise_notImplementedError(self):
        network_socket: NetworkSocket = commons.create_socket("localhost", 10_000)
        with pytest.raises(NotImplementedError) as _:
            network_socket.broadcast("my-message")