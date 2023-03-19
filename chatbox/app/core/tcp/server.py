import json
import logging
import socket
import time
import threading
import queue
import uuid
from typing import Type

from .network_socket import NetworkSocket
from chatbox.app import constants
from chatbox.app.constants import chat_internal_codes as codes

_logger = logging.getLogger(__name__)


class SocketTCPServer(NetworkSocket):
    SOCKET_TYPE: str = "tcp_server"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        self._server_listening: bool = False # server is currenly listenning for new client connection # TODO: Make setter for these flags value! (USe bitwise as well?)TODO: Semaphore or signal?

        # TODO : 1 thred-safe | 2. make queue
        self.client_messages : queue.Queue[dict[str, str]] = queue.Queue(maxsize=constants.SOCKET_MAX_MESSAGE_QUEUE_PER_WORKER)
        self.clients_undentified: dict = {}
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
                client, address = self.socket.accept()   # blocking - main thread
                total_client_connected += 1

                client_memory_id = id(client)
                client_identifier = hash((address, client_memory_id))
                self.clients_undentified[client_identifier] = { # TODO . make class client (and Connection and Server)
                    'client': client,
                    'client_identifier': client_identifier,
                    'client_memory_id': client_memory_id,
                    'address': address,
                    'user_id': str(uuid.uuid4()),
                    'cliefnt_fd': client.fileno(),
                    'state': 'unknown'
                }

                client_name_unknown = f'New connection {address} | client_identifier={client_identifier}, waiting for identity'
                _logger.info(client_name_unknown)

                t_receiver = threading.Thread(target=self.thread_receiver, args=(client_identifier, self.clients_undentified[client_identifier]), daemon=True)
                t_broadcaster = threading.Thread(target=self.thread_broadcaster, daemon=True)

                t_receiver.start()
                t_broadcaster.start()

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
            raise Exception("EXCEPTION TODO!!!!!") # TODO Here !
        client_address = client_data.get("address", "Unknown")
        user_id = client_data.get("user_id", None)
        name = f"{client_identifier} @ {client_address} -- "
        _logger.info(f'{name} start receiving ....')
        logged_in: bool = False
        exception: BaseException | None = None
        try:
            with client:
                try:
                    while True:
                        message = self.receive(client)  # blocking - t_receiver
                        if not message:
                            break
                        _logger.info(f"[RECEIVED]::({name}) >>> {message}")
                        if logged_in:
                            message = f'-- {client_data["user_name"]} :: {message}'
                            self.client_messages.put({client_identifier: message})
                            # t_broadcast = threading.Thread(target=self.thread_broadcast, args=(message, client_identifier), daemon=True)
                            # t_broadcast.start()
                            continue

                        logging_code_type = codes.code_in(codes.LOGIN, message) or codes.code_in(codes.IDENTIFICATION, message)
                        logged_in = self.login(logging_code_type, message, user_id, client_data, client_identifier, name)
                        if not logged_in:
                            _logger.info(f"Client {name} not identified, sending identification token") # todo what to send??
                            self.send(client, codes.make_message(codes.IDENTIFICATION_REQUIRED, user_id))

                    _logger.warning(f"{name} receive a close network socket message, closing socket... ")
                except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                    _logger.error(f"Connection in receiver thread, reason: {error}")
                    out_message = "[I/O_ERROR_CONNECTION] - Connection error"
                    exception = error

                except BaseException as error:
                    out_message = f"{error.__class__.__name__} - Something went wrong"
                    exception = error
                else:
                    _logger.debug(f"{name} closing connection ...")
                finally:
                    if exception:
                        _logger.error(f"{name} closing connection ... {out_message} in receiver thread, reason: {exception}")
                        raise exception
        except BaseException as base_error:
            _logger.debug(f'while handling client encountered a BaseException, reason {base_error}')
        finally:
            if client_identifier in self.clients_undentified:
                del self.clients_undentified[client_identifier]
                _logger.debug(f"Delete {client_identifier} from clients_undentified")
            if client_identifier in self.clients_identified:
                del self.clients_identified[client_identifier]
                _logger.debug(f"Delete {client_identifier} from clients_identified")
        # TODO:
        # 1 identify client
        # 2 when identified remove from identify and add to known client
        # 3 if error remove client from known/unknown clients
        # exit gracefull,and capture corerct errors
        # add sender thread
        # Implement queue for message to broadcast

    def thread_broadcaster(self) -> None:
        while self.server_listening: # TODO: check if is better add anotehr flag instead of server_listening
            message_to_broadcast = self.client_messages.get()   # blocking - t_broadcaster
            client_identifier = list(message_to_broadcast.keys())
            if client_identifier:
                client_identifier = client_identifier[0]
                message = message_to_broadcast[client_identifier]
                self.broadcast(client_identifier, message)
            self.client_messages.task_done()

    def broadcast(self, client_identifier: str, message: str) -> None:
        for identifier in self.clients_identified:
            if identifier == client_identifier:
                continue
            client_info = self.clients_identified[identifier]
            self.send(client_info['client'], message)

    def start_listening(self):
        self.server_listening = True

    def stop_listening(self):
        self.server_listening = False


    # ------------------------------------
    # Business Logic
    # ------------------------------------
    def login(self, logging_code_type: int, payload: str, user_id: str, client_data: dict, client_identifier: str, name: str) -> bool:
        if not logging_code_type:
            return False
        login_info = self.parse_json(codes.get_message(logging_code_type, payload))
        if not login_info:
            return False

        input_user_id = login_info.get('user_id', None)
        input_user_name = login_info.get('user_name', None)
        _logger.info(f"{input_user_name} - with user_id {input_user_id} request LOGIN")

        if input_user_id != user_id:  # TODO: check password!!!!
            return False

        if not input_user_name:
            return False

        client_data['user_name'] = input_user_name
        client_data['login_info'] = login_info
        client_data['state'] = 'logged'
        self.clients_identified[client_identifier] = client_data  # add client to identify
        del self.clients_undentified[client_identifier] # remove client from un-identify one

        _logger.info(f"Client {name} identified with credentials {login_info}")
        return True
