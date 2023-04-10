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
import threading
import time

import pytest

from chatbox.app.core.tcp.network_socket import NetworkSocket
from chatbox.app import constants

from tests.conftest import TCPSocketMock, lock


class TestNetworkSocket:

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    @pytest.mark.parametrize('network_socket', [{'host': 'localhost', 'port': 10_000}], indirect=True)   # NOTE: kept parametrize for reference
    def test_net_socket_instance_constructor(self, network_socket):
        assert type(network_socket.socket) is socket.socket

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_get_app_host_get_default(self):
        my_host = constants.SOCKET_HOST_DEFAULT
        expected = socket.gethostbyname(socket.gethostname())

        app_host = NetworkSocket.get_app_host(my_host)

        assert app_host == expected

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_get_app_host_custom(self):
        my_host = "199.123.180.20"

        app_host = NetworkSocket.get_app_host(my_host)

        assert my_host == app_host

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_create_tcp_socket(self, _socket):
        assert type(_socket) is socket.socket
        assert isinstance(_socket, socket.socket)
        assert isinstance(_socket, socket.socket)

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_socket_connect_returns_false_because_is_abstract(self, network_socket):
        network_socket: NetworkSocket = network_socket
        connected: bool = network_socket.socket_connect()
        assert connected is False

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_run_network_socket_raise_because_is_abstract(self, network_socket):
        network_socket: NetworkSocket = network_socket
        with pytest.raises(Exception) as _:
            network_socket()

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_wait_or_die(self, network_socket):
        seconds_to_wait = 3
        seconds_to_trigger_close = 2  # manually 'close' the NetworkSocket so that wait_or_die must stop and call close to self

        network_socket: NetworkSocket = network_socket
        network_socket.socket_connected.set()  # mock that the server is connected

        waiting_thread = threading.Thread(target=network_socket.start_wait_forever, daemon=True)  # let's put it in a thread in order to monitor it
        waiting_thread.start()

        while seconds_to_wait:
            time.sleep(1)
            seconds_to_wait -= 1
            if seconds_to_trigger_close == seconds_to_wait:
                network_socket.stop_wait_forever()

        assert network_socket.socket_connected.is_set() is False

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_overridable_functions_must_return_notImplemented(self, network_socket):
        network_socket: NetworkSocket = network_socket

        assert network_socket.socket_on_before() is NotImplemented
        assert network_socket.socket_on_after(network_socket.socket) is NotImplemented
        assert network_socket.start_before() is NotImplemented
        assert network_socket.start_after() is NotImplemented
        assert network_socket.start() is NotImplemented
        assert network_socket.close_before() is NotImplemented
        assert network_socket.close_after() is NotImplemented

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_overridable_functions_raise_notImplementedError(self, network_socket):
        network_socket: NetworkSocket = network_socket
        client_identifier = hash((network_socket.socket.getsockname(), id(network_socket)))
        with pytest.raises(NotImplementedError) as _:
            network_socket.broadcast(client_identifier, "my-message")

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_encode_message(self):
        message: str = "hello world"

        message_encoded: bytes = NetworkSocket.encode_message(message)

        assert isinstance(message_encoded, bytes)

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_encode_message_error_attribute(self):
        message: int = 123

        with pytest.raises(AttributeError) as _:
            NetworkSocket.encode_message(message) # noqa

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_decode_message(self):
        message: bytes = b'hello world'

        message_decoded: str = NetworkSocket.decode_message(message)

        assert isinstance(message_decoded, str)

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_decode_message_error_attribute(self):
        message: int = 123

        with pytest.raises(AttributeError) as _:
            NetworkSocket.decode_message(message) # noqa

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_receive(self, network_socket, _socket):
        address: tuple[str, int] = ("localhost", 10_000)

        server: NetworkSocket = network_socket   # noqa

        TCPSocketMock.manual_connect(server.socket, address, "tcp_server")   # noqa
        TCPSocketMock.manual_connect(_socket, address, "tcp_client")

        data_dummy = "hello world"
        data_received: dict = {"data": None}

        server_t = threading.Thread(target=TCPSocketMock.mock_server_listen_once, args=(server.socket, server.receive, data_received), daemon=True)
        client_t = threading.Thread(target=TCPSocketMock.socket_send, args=(_socket, data_dummy), daemon=True)

        server_t.start()
        client_t.start()

        server_t.join()
        client_t.join()

        assert data_received['data'] == data_dummy

    @pytest.mark.tcp_core
    @pytest.mark.tcp
    def test_net_socket_send(self, network_socket, _socket):
        address: tuple[str, int] = ("localhost", 10_001)

        server: NetworkSocket = network_socket   # noqa

        TCPSocketMock.manual_connect(server.socket, address, "tcp_server")   # noqa
        TCPSocketMock.manual_connect(_socket, address, "tcp_client")

        data_dummy = "hello world"
        data_received: dict = {"data": None}

        server_listen_t = threading.Thread(target=TCPSocketMock.mock_server_send_once, args=(server.socket, server.send, data_dummy), daemon=True)
        client_t = threading.Thread(target=TCPSocketMock.mock_receiver, args=(_socket, data_received), daemon=True)

        server_listen_t.start()
        client_t.start()

        server_listen_t.join()
        client_t.join()

        with lock:
            assert data_received['data'] == data_dummy
