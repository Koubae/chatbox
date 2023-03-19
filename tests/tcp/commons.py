import time

import pytest
import socket
import threading

from chatbox.app.core.tcp.network_socket import NetworkSocket

pytestmark = [pytest.mark.tcp_core, pytest.mark.tcp]
lock = threading.Lock()
sockets_created: list[NetworkSocket] = []


def create_socket(*args, **kwargs) -> NetworkSocket:
    network_socket = NetworkSocket(*args, **kwargs)
    sockets_created.append(network_socket)
    return network_socket


def teardown_module(_):
    """teardown any state that was previously setup with a setup_module method."""
    for _socket in sockets_created:
        _socket.terminate()

def manual_connect(socket: socket.socket, address: tuple, socket_type: str = "tcp_server") -> bool:
    """Manually connect the socket for unittesting"""
    try:
        if socket_type == "tcp_server":
            socket.bind(address)
            socket.listen(5)
        elif socket_type == "tcp_client":
            socket.connect(address)
        else:
            return False
    except (ConnectionRefusedError, ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError, ConnectionError) as error:
        print("Error while establishing connection to %s, reason : %s" % (address, error))
        return False
    else:

        return True


def mock_server_listen_once(server: socket.socket, receiver, output: dict):
    client_conn, _ = server.accept()
    with client_conn:
        data = receiver(client_conn)
        with lock:
            output["data"] = data

def mock_server_send_once(server: socket.socket, sender, data: str):
    client_conn, _ = server.accept()
    with client_conn:
        _ = sender(client_conn, data)

def mock_receiver(_socket: socket.socket, output: dict):
    data = None
    while not data:
        data = _socket.recv(1024)
        if data:
            with lock:
                output["data"] = data.decode('utf-8')
                break

def mock_socket_send(_socket: socket.socket, msg: str):
    _socket.send(msg.encode('utf-8'))