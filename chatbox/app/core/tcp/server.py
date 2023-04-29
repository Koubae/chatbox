import logging
import socket
import threading
import queue
import uuid


from chatbox.app import constants
from chatbox.app.constants import chat_internal_codes as codes
from .network_socket import NetworkSocket
from . import objects


_logger = logging.getLogger(__name__)


class SocketTCPServer(NetworkSocket):
    SOCKET_TYPE: str = "tcp_server"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        self.server_session: uuid.UUID = uuid.uuid4() # TODO. 1. send to client. create session expiration . save sesison to db. session data should be a pickled object using shelfe?
        self._server_listening: bool = False

        self.client_messages : queue.Queue[objects.Message] = queue.Queue(maxsize=constants.SOCKET_MAX_MESSAGE_QUEUE_PER_WORKER)
        self.clients_undentified: dict[int, objects.Client] = {}
        self.clients_identified: dict[int, objects.Client] = {}

        # metadata
        self.total_client_connected: int = 0

    def start(self):
        exception: BaseException|None = None

        self.start_listening()
        threading.Thread(target=self.thread_broadcaster, daemon=True).start()
        while self.server_listening:
            try:
                client, address = self.socket.accept()   # blocking - main thread
                self.accept_new_connection(client, objects.Address(*address))
            except KeyboardInterrupt as error:
                _logger.warning(f"Interrupted by User while accepting new client connections, reason: {error}")
                self.stop_listening()
            except SystemExit as error:
                _logger.warning(f"Interrupted by System while accepting new client connections, reason: {error}")
                self.stop_listening()
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                _logger.warning(f"Connection error while accepting new client connections, reason: {error}")
                self.stop_listening()
            except OSError as error:
                _logger.warning(f"OSError error while accepting new client connections, reason: {error}")
                exception = error
                self.stop_listening()
            finally:
                if exception:
                    raise exception from None

        else:
            _logger.warning(f"Exit naturally, total_client_connected={self.total_client_connected}")

    def close_before(self):
        self.stop_listening()

    def thread_client_receiver(self, client_conn: objects.Client):
        _logger.info(f'{client_conn} receiving ....')

        exception: BaseException | None = None
        try:
            with client_conn.connection:
                try:
                    while True:
                        message = self.receive(client_conn.connection)  # blocking - t_receiver
                        if not message:
                            break

                        if not client_conn.is_logged():
                            self.login_request(client_conn, message)
                            continue

                        self.add_message_to_broadcast(client_conn, message)

                    _logger.warning(f"{client_conn} receive a close network socket message, closing socket... ")
                except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                    _logger.error(f"Connection in receiver thread, reason: {error}")
                    out_message = "[I/O_ERROR_CONNECTION] - Connection error"
                    exception = error

                except BaseException as error:
                    out_message = f"{error.__class__.__name__} - Something went wrong"
                    exception = error
                else:
                    _logger.debug(f"{client_conn} closing connection ...")
                finally:
                    if exception:
                        _logger.error(f"{client_conn} closing connection ... {out_message} in receiver thread, reason: {exception}")
                        raise exception
        except BaseException as base_error:
            _logger.debug(f'while handling client encountered a BaseException, reason {base_error}')
        finally:
            if client_conn.identifier in self.clients_undentified:
                del self.clients_undentified[client_conn.identifier]
                _logger.debug(f"Delete {client_conn.identifier} from clients_undentified")
            if client_conn.identifier in self.clients_identified:
                del self.clients_identified[client_conn.identifier]
                _logger.debug(f"Delete {client_conn.identifier} from clients_identified")

    def thread_broadcaster(self) -> None:
        while self.server_listening:
            message_to_broadcast: objects.Message = self.client_messages.get()   # blocking - t_broadcaster
            client_identifier = message_to_broadcast['identifier']
            message = message_to_broadcast['message']
            send_all = message_to_broadcast['send_all']
            if client_identifier and message:
                self.broadcast(client_identifier, message, send_all=send_all)
            self.client_messages.task_done()

    def broadcast(self, client_identifier: int, message: str, send_all: bool = False) -> None:
        clients_to_send = self.clients_identified
        if send_all:
            clients_to_send = {**clients_to_send, **self.clients_undentified}

        for identifier in clients_to_send:
            client_conn: objects.Client = clients_to_send[identifier]
            client_socket: socket.socket = client_conn.connection
            self.send(client_socket, message)

    def start_listening(self):
        self.server_listening = True

    def stop_listening(self):
        self.server_listening = False

    def accept_new_connection(self, client: socket.socket, address: objects.Address) -> None:
        self.total_client_connected += 1

        new_connection = self.create_client_object(client, address)
        self.clients_undentified[new_connection.identifier] = new_connection

        _logger.info(f'New connection {new_connection} accepted, creating receiving client thread')
        t_receiver = threading.Thread(target=self.thread_client_receiver, args=(new_connection,), daemon=True)
        t_receiver.start()

    # ------------------------------------
    # Business Logic
    # ------------------------------------
    def login_request(self, client_conn: objects.Client, payload: str) -> bool:
        logging_code_type = codes.code_in(codes.LOGIN, payload) or codes.code_in(codes.IDENTIFICATION, payload)
        logged_in = self.login(logging_code_type, client_conn, payload)
        if not logged_in:
            _logger.info(f"Client {client_conn} not identified, requesting identification and sending user_id")
            self.send(client_conn.connection, codes.make_message(codes.IDENTIFICATION_REQUIRED, client_conn.user_id))
            return False

        self.send(client_conn.connection, codes.make_message(codes.LOGIN_SUCCESS, str(self.server_session)))
        return True

    def login(self, logging_code_type: int, client_conn: objects.Client, payload: str) -> bool:
        if not logging_code_type or not client_conn or not payload:
            return False
        if client_conn.identifier not in self.clients_undentified:
            return False
        login_info = self.parse_json(codes.get_message(logging_code_type, payload))
        if not login_info:
            return False

        input_user_id = login_info.get('user_id', None)
        input_user_name = login_info.get('user_name', None)
        input_user_password = login_info.get('password', None)
        if not input_user_id or not input_user_name or not input_user_password:
            return False

        _logger.info(f"{client_conn.user_name} - with user_id {client_conn.user_id} request {codes.CODES[logging_code_type]}")
        # TODOs:
        # 1. db : select user from db if exist
        # 2. db: create user from db if not exist
        # 3. db. update user loggins status
        # 3. check password
        # 4. save encrypt saved password
        # 5. Send 'session' to client (which the client can save) if session is the same! with expiration!!!
        if input_user_id != client_conn.user_id:
            return False

        # TODO: check password!!!!
        if input_user_password != input_user_password:
            return False


        client_conn.user_name = input_user_name
        client_conn.login_info = login_info
        client_conn.set_logged_in()

        self.clients_identified[client_conn.identifier] = client_conn  # add client to identify
        del self.clients_undentified[client_conn.identifier]           # remove client from un-identify one

        _logger.info(f"Client {client_conn} identified with credentials {login_info}")
        return True

    def add_message_to_broadcast(self, client_conn: objects.Client, message: str, send_all: bool = False) -> None:
        _logger.info(f"[RECEIVED]::({client_conn}) to broadcast >>> {message}")
        message = f'-- {client_conn.user_name} :: {message}'
        self.client_messages.put({'identifier': client_conn.identifier, 'message': message, 'send_all': send_all})

    # ------------------------------------
    # Getter and setters
    # ------------------------------------
    @property
    def server_listening(self) -> bool:
        return self._server_listening  # pragma: no cover

    @server_listening.getter
    def server_listening(self) -> bool:
        return self._server_listening

    @server_listening.setter
    def server_listening(self, value: bool) -> None:
        if not isinstance(value, (bool, int)):
            raise TypeError(f"Value for server_listening must be of type (bool, int), {type(value)} passed")
        self._server_listening = value

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------
    def create_client_object(self, client: socket.socket, address: objects.Address) -> objects.Client:
        client_identifier = self.create_client_identifier(client, address)
        return objects.Client(
            client,
            client_identifier['identifier'],
            client_identifier['id'],
            address,
            uuid.uuid4()
        )

    @staticmethod
    def create_client_identifier(client: socket.socket, address: objects.Address) -> dict[str, int]:
        client_memory_id = id(client)
        client_identifier = hash((address, client_memory_id))
        return {'id': client_memory_id, 'identifier': client_identifier}
