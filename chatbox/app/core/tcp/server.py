import logging
import socket
import threading
import queue
import uuid

from chatbox.app import constants
from chatbox.app.constants import DIR_DATABASE_SCHEMA_MAIN, DIR_DATABASE_MAIN, DIR_DATABASE_DATA_MAIN
from .network_socket import NetworkSocket
from ..components.server.router import Router, RouterStopRoute
from ..model.message import MessageDestination, MessageRole, ServerMessageModel
from ..model.server_session import ServerSessionModel
from . import objects
from ...database.orm.sqlite_conn import SQLITEConnection
from ...database.repository.channel import ChannelRepository, ChannelMemberRepository
from ...database.repository.group import GroupRepository
from ...database.repository.server_session import ServerSessionRepository
from ...database.repository.user import UserRepository, UserLoginRepository
from ...database.repository.message import MessageRepository

_logger = logging.getLogger(__name__)


class SocketTCPServer(NetworkSocket):
    SOCKET_TYPE: str = "tcp_server"

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        self._server_listening: bool = False
        self.client_messages: queue.Queue[ServerMessageModel] = queue.Queue(maxsize=constants.SOCKET_MAX_MESSAGE_QUEUE_PER_WORKER)
        self.clients_unidentified: dict[int, objects.Client] = {}
        self.clients_identified: dict[int, objects.Client] = {}
        # Routers
        self.router: Router = Router(self)
        # metadata
        self.total_client_connected: int = 0
        # DATABASE
        self.server_session: ServerSessionModel | None = None
        self._init_database()

    def __del__(self):
        super().__del__()
        try:
            self.database.__del__()
            del self.database
        except AttributeError:
            pass
        except Exception as error:
            _logger.exception(f"An exception occurred while closing connection to database, error {error}", exc_info=error)

    def _init_database(self):
        self.database: SQLITEConnection = self._connect_to_database()
        # TODO: make a repo pool !
        self.repo_server: ServerSessionRepository = ServerSessionRepository(self.database)
        self.repo_user: UserRepository = UserRepository(self.database)
        self.repo_user_login: UserLoginRepository = UserLoginRepository(self.database)
        self.repo_message: MessageRepository = MessageRepository(self.database)
        self.repo_group: GroupRepository = GroupRepository(self.database)
        self.repo_channel_member: ChannelMemberRepository = ChannelMemberRepository(self.database)
        self.repo_channel: ChannelRepository = ChannelRepository(self.database, repo_channel_member=self.repo_channel_member)
        self.server_session: ServerSessionModel = self.repo_server.get_session_or_create()

    @staticmethod
    def _connect_to_database() -> SQLITEConnection:
        return SQLITEConnection(DIR_DATABASE_MAIN, schema=DIR_DATABASE_SCHEMA_MAIN, data=DIR_DATABASE_DATA_MAIN)

    def start(self):
        exception: BaseException | None = None

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
                        message: ServerMessageModel = self.receive_message(client_conn)  # blocking - t_receiver
                        if not message:
                            break

                        try:
                            self.router.route(client_conn, message)
                        except RouterStopRoute:
                            break

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
            if client_conn.identifier in self.clients_unidentified:
                del self.clients_unidentified[client_conn.identifier]
                _logger.debug(f"Delete {client_conn.identifier} from clients_unidentified")
            if client_conn.identifier in self.clients_identified:
                del self.clients_identified[client_conn.identifier]
                _logger.debug(f"Delete {client_conn.identifier} identifier = {getattr(client_conn, '_identifier')} from clients_identified")

    def thread_broadcaster(self) -> None:
        while self.server_listening:
            message_to_broadcast: ServerMessageModel = self.client_messages.get()   # blocking - t_broadcaster
            self.repo_message.create_new_message(self.server_session.id, message_to_broadcast)  # TODO: check peformance.

            self.broadcast(message_to_broadcast)
            self.client_messages.task_done()

    # TODO:
    # 1. There is something a RuntimeError (dictionary change size during iteration)
    def broadcast(self, message: ServerMessageModel) -> None:
        to: MessageDestination = message.to

        match to.role:
            case MessageRole.USER:
                clients_to_send = {}
                user = next((user for identifier, user in self.clients_identified.items() if identifier == to.identifier), None)
                if user:
                    clients_to_send[to.identifier] = user
            case MessageRole.GROUP | MessageRole.CHANNEL:
                members = to.users
                clients_to_send = {identifier: user for identifier, user in self.clients_identified.items() if user.user_name in members}

            case MessageRole.ALL:
                clients_to_send = {**self.clients_identified, **self.clients_unidentified}
            case _:
                clients_to_send = {**self.clients_identified, **self.clients_unidentified}

        for identifier in clients_to_send:
            client_conn: objects.Client = clients_to_send[identifier]
            client_socket: socket.socket = client_conn.connection
            self.send_message(client_socket, message)

    def receive_message(self, client_conn: objects.Client, buffer_size: int = constants.SOCKET_STREAM_LENGTH) -> ServerMessageModel | None:
        message: str = self.receive(client_conn.connection, buffer_size)
        if not message:
            return

        message: ServerMessageModel = ServerMessageModel.from_json(message)
        if not message:
            return
        message.owner = MessageDestination(
            identifier=client_conn.user and client_conn.user.id or client_conn.user_id,
            name=client_conn.user_name,
            role=MessageRole.USER
        )
        return message

    def send_message(self, connection: socket.socket, message: ServerMessageModel) -> int:
        return self.send(connection, message.to_json())

    def start_listening(self):
        self.server_listening = True

    def stop_listening(self):
        self.server_listening = False

    def accept_new_connection(self, client: socket.socket, address: objects.Address) -> None:
        self.total_client_connected += 1

        new_connection = self.create_client_object(client, address)
        self.clients_unidentified[new_connection.identifier] = new_connection

        _logger.info(f'New connection {new_connection} accepted, creating receiving client thread')
        t_receiver = threading.Thread(target=self.thread_client_receiver, args=(new_connection,), daemon=True)
        t_receiver.start()

    # ------------------------------------
    # Business Logic
    # ------------------------------------
    def add_message_to_broadcast(self, client_conn: objects.Client, message: ServerMessageModel) -> None:
        _logger.info(f"[RECEIVED]::({client_conn}) to broadcast >>> {message.body}")
        self.client_messages.put(message)

    def send_to_client(self, client_conn: objects.Client, payload: str) -> None:
        sender = MessageDestination(self.server_session.session_id, name=self.name, role=MessageRole.SERVER)
        to = MessageDestination(client_conn.user and client_conn.user.id or client_conn.user_id, name=self.name, role=MessageRole.USER)
        message = ServerMessageModel.new_message(sender, sender, to, payload)

        self.send_message(client_conn.connection, message)

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
