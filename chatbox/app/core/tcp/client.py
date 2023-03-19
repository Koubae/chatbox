import logging
from typing import Type

from .network_socket import NetworkSocket


_logger = logging.getLogger(__name__)


class SocketTCPClient(NetworkSocket):
    SOCKET_TYPE: str = "tcp_client"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        self._connected_to_server: bool = False # currently connected to the server # TODO: Make setter for these flags value! (USe bitwise as well?)TODO: Semaphore or signal?

    @property
    def connected_to_server(self) -> bool:
        return self._connected_to_server

    @connected_to_server.getter
    def connected_to_server(self) -> bool:
        return self._connected_to_server

    @connected_to_server.setter
    def connected_to_server(self, value: bool) -> None:
        if not isinstance(value, (bool, int)):
            raise TypeError(f"Value for connected_to_server must be of type (bool, int), {type(value)} passed")
        self._connected_to_server = value

    def start(self):
        exception_to_raise: list[Type[BaseException], ...] = [KeyboardInterrupt, KeyboardInterrupt, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError]
        exception: BaseException | None = None
        self.start_connecting_to_server()
        while self.connected_to_server:
            try:
                while True:
                    message: str = input(">>> ")
                    self.socket.send(message.encode('utf-8'))

                    echoed = self.socket.recv(1024)
                    _logger.info("Server replied : %s", echoed.decode("utf-8"))

            except KeyboardInterrupt as error:
                _logger.warning(f"Interrupted by User, reason: {error}")
                exception = error
            except SystemExit as error:
                _logger.warning(f"Interrupted by System, reason: {error}")
                exception = error
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                _logger.warning(f"Network Connection error to the server, reason: {error}")
                exception = error
                if error.__class__ not in exception_to_raise:
                    _logger.warning(f"Exception of type {error.__class__} no inside exception_to_raise, adding it programmatically")
                    exception_to_raise.append(error.__class__)
            finally:
                if exception and exception.__class__ in exception_to_raise:
                    self.stop_connecting_to_server()
                    raise exception from None

        else:
            _logger.warning(f"Exit naturally")

    def start_connecting_to_server(self):
        self.connected_to_server = True

    def stop_connecting_to_server(self):
        self.connected_to_server = False