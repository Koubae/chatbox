from .network_socket import NetworkSocket

class SocketTCPServer(NetworkSocket):
    SOCKET_TYPE: str = "tcp_server"

    def start(self): ...
