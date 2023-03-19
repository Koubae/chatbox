import pytest
from chatbox.app.core.tcp.network_socket import NetworkSocket

pytestmark = [pytest.mark.tcp_core, pytest.mark.tcp]

sockets_created: list[NetworkSocket] = []


def create_socket(*args, **kwargs) -> NetworkSocket:
    network_socket = NetworkSocket(*args, **kwargs)
    sockets_created.append(network_socket)
    return network_socket


def teardown_module(_):
    """teardown any state that was previously setup with a setup_module method."""
    for _socket in sockets_created:
        _socket.terminate()
