from .network_socket import NetworkSocket

class SocketTCPClient(NetworkSocket):
    SOCKET_TYPE: str = "tcp_client"