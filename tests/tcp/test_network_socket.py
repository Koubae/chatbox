import sys
import socket
import pytest
from chatbox.app.core.tcp.network_socket import NetworkSocket
from chatbox.app import constants


sockets_created: list[NetworkSocket] = []

def create_socket(*args, **kwargs) -> NetworkSocket:
    network_socket = NetworkSocket(*args, **kwargs)
    sockets_created.append(network_socket)
    return network_socket

def teardown_module(_):
    """teardown any state that was previously setup with a setup_module method."""
    for _socket in sockets_created:
        _socket.terminate()

class TestNetworkSocket:

    def test_instance_constructor(self):
        network_socket = create_socket("localhost", 10_000)
        assert type(network_socket.socket) is socket.socket

    def test_get_app_host_get_default(self):
        my_host = constants.SOCKET_HOST_DEFAULT
        expected = socket.gethostbyname(socket.gethostname())

        app_host = NetworkSocket.get_app_host(my_host)

        assert  app_host == expected

    def test_get_app_host_custom(self):
        my_host = "199.123.180.20"

        app_host = NetworkSocket.get_app_host(my_host)

        assert my_host == app_host

    def test_create_tcp_socket(self):
        socket_options = [(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)]

        _socket = NetworkSocket.create_tcp_socket(socket_options)

        assert type(_socket) is socket.socket
        assert isinstance(_socket, socket.socket)
        assert isinstance(_socket, socket.socket)
