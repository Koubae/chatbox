import socket


def get_local_ipaddr() -> str:
    """Get the default IP Address of the host machine"""
    return socket.gethostbyname(socket.gethostname())


def create_tcp_socket(address: tuple[str, int], server_type: str = "server") -> socket.socket:
    """
        Creates a simple TCP Socket
    :param address: Tuple containing the host, port : Host example 127.0.0.1  |  Port example 8080
    :param server_type: server | client
    :return: A new Socket instance bind with the given (host, port) address
    """
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if server_type == "client":
        socket_connection.connect(address)
    else:
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        socket_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_connection.bind(address)
    return socket_connection

