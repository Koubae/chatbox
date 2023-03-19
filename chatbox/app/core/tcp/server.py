import json
import logging
import socket
import time
import threading
import uuid
from typing import Type

from .network_socket import NetworkSocket
from chatbox.app.constants import chat_internal_codes as codes

_logger = logging.getLogger(__name__)


class SocketTCPServer(NetworkSocket):
    SOCKET_TYPE: str = "tcp_server"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        self._server_listening: bool = False # server is currenly listenning for new client connection # TODO: Make setter for these flags value! (USe bitwise as well?)TODO: Semaphore or signal?

        # TODO : 1 thred-safe | 2. make queue
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
                client, address = self.socket.accept()
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
                t_receiver = threading.Thread(target=self.thread_receiver, args=(client_identifier, self.clients_undentified[client_identifier]))
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
            raise Exception("EXCEPTION TODO!!!!!") # TODO Here !
        client_address = client_data.get("address", "Unknown")
        user_id = client_data.get("user_id", None)
        name = f"{client_identifier} @ {client_address} -- "
        _logger.info(f'{name} start receiving ....')
        identified: bool = False
        exception: BaseException | None = None
        try:
            with client:
                try:
                    while True:
                        message = self.receive(client)
                        if not message:
                            break
                        _logger.info(f"[RECEIVED]::({name}) >>> {message}")
                        requested_login = codes.code_in(codes.LOGIN, message)
                        if not identified or requested_login:
                            identification_required = True
                            if requested_login:
                                login_info = json.loads(codes.get_message(codes.LOGIN, message))
                                payload_user_id = login_info.get('user_id', None)
                                user_name = login_info.get('user_name', None)
                                _logger.info(f"{user_name} request LOGIN")
                                if payload_user_id == user_id:
                                    if user_name:
                                        identification_required = False
                                        # add client to identified one
                                        # TODO: make db storage - persistance  , remember clients
                                        client_data['user_name'] = user_name
                                        client_data['login_info'] = login_info
                                        self.clients_identified[client_identifier] = client_data
                                        # remove client from un-identify one
                                        del self.clients_undentified[client_identifier]
                                        identified = True
                                        _logger.info(f"Client {name} identified with credentials {login_info}")
                            elif codes.code_in(codes.IDENTIFICATION, message):
                                login_info = json.loads(codes.get_message(codes.IDENTIFICATION, message)) # TODO: check that same token is the same
                                user_name = login_info.get('user_name', None)
                                password = login_info.get('password', None)
                                payload_user_id = login_info.get('user_id', None)
                                _logger.info(f"{user_name} request {codes.IDENTIFICATION}")
                                if payload_user_id == user_id:
                                    if user_name:
                                        identification_required = False
                                        # add client to identified one
                                        # TODO: make db storage - persistance  , remember clients
                                        client_data['user_name'] = user_name
                                        client_data['login_info'] = login_info
                                        self.clients_identified[client_identifier] = client_data
                                        # remove client from un-identify one
                                        del self.clients_undentified[client_identifier]
                                        identified = True
                                        _logger.info(f"Client {name} identified with credentials {login_info}")
                            if identification_required:
                                _logger.info(f"Client {name} not identified, sending identification token") # todo what to send??
                                self.send(client, codes.make_message(codes.IDENTIFICATION_REQUIRED, user_id))
                        else:
                            self.broadcast(message, from_client=client_identifier)
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

    def broadcast(self, message: str, from_client: str|None = None) -> None:
        for client_identifier in self.clients_identified:
            if client_identifier == from_client:
                continue
            client_info = self.clients_identified[client_identifier]
            self.send(client_info['client'], message)

    def start_listening(self):
        self.server_listening = True

    def stop_listening(self):
        self.server_listening = False



