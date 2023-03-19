import logging
import time
import threading
import uuid
from typing import Type

from .network_socket import NetworkSocket


_logger = logging.getLogger(__name__)


class SocketTCPServer(NetworkSocket):
    SOCKET_TYPE: str = "tcp_server"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        self._server_listening: bool = False # server is currenly listenning for new client connection # TODO: Make setter for these flags value! (USe bitwise as well?)TODO: Semaphore or signal?

        # TODO : 1 thred-safe | 2. make queue
        self.clients_unknown: dict = {}
        self.clients_identified: dict = {}

    @property
    def server_listening(self) -> bool:
        return self._server_listening

    @server_listening.getter
    def server_listening(self) -> bool:
        return self._server_listening

    @server_listening.setter
    def server_listening(self, value: bool) -> None:
        if not isinstance(value, (bool, int)):
            raise TypeError(f"Value for server_listening must be of type (bool, int), {type(value)} passed")
        self._server_listening = value

    def start(self):
        total_client_connected = 0
        exception_to_raise: tuple[Type[BaseException], ...] = (KeyboardInterrupt, KeyboardInterrupt)
        exception: BaseException|None = None

        self.start_listening()
        while self.server_listening:
            try:
                client, address = self.socket.accept()
                total_client_connected += 1

                client_id = id(client)
                client_identifier = hash((address, client_id))
                self.clients_unknown[client_identifier] = {
                    'client': client,
                    'client_identifier': client_identifier,
                    'client_id': client_id,
                    'address': address,
                    'client_token': uuid.uuid4(),
                    'client_fd': client.fileno(),
                    'state': 'unknown'
                }

                client_name_unknown = f'New connection {address} | client_identifier={client_identifier}, waiting for identity'
                _logger.info(client_name_unknown)
                t_receiver = threading.Thread(target=self.thread_receiver, args=(client_identifier, self.clients_unknown[client_identifier]))
                t_receiver.start()

            except KeyboardInterrupt as error:
                _logger.warning(f"Interrupted by User while accepting new client connections, reason: {error}")
                exception = error
            except SystemExit as error:
                _logger.warning(f"Interrupted by System while accepting new client connections, reason: {error}")
                exception = error
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                _logger.warning(f"Connection error while accepting new client connections, reason: {error}")
                exception = error
            finally:
                if exception and exception.__class__ in exception_to_raise:
                    self.stop_listening()
                    raise exception from None

        else:
            _logger.warning(f"Exit naturally, total_client_connected={total_client_connected}")

    def thread_receiver(self, client_identifier: str, client_data: dict): # TODO add as NotImplemented in class mother
        client = client_data.get('client', None)
        if not client:
            raise Exception("EXCEPTION TODO!!!!!")
        client_address = client_data.get("address", "Unknown")
        name = f"{client_identifier} @ {client_address} -- "
        _logger.info(f'{name} start receiving ....')
        with client:
            try:
                while True:
                    data = client.recv(1024)
                    if not data:
                        break
                    mgs = data.decode("utf-8")
                    _logger.info(f"{client_address} >>> {mgs}")
                    client.send(data)
                _logger.info(f"{name} stop receiving, socket closed")
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                _logger.warning(f"Connection error while accepting new client connections, reason: {error}")
                exception = error
                raise error  # TODO

        # TODO:
        # 1 identify client
        # 2 when identified remove from identify and add to known client
        # 3 if error remove client from known/unknown clients
        # exit gracefull,and capture corerct errors
        # add sender thread

    def start_listening(self):
        self.server_listening = True

    def stop_listening(self):
        self.server_listening = False



