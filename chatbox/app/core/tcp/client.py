import json
import logging
import socket
import threading
import queue
import time

from chatbox.app import constants
from chatbox.app.constants import chat_internal_codes as _c
from .network_socket import NetworkSocket
from . import objects
from ..components.client.auth import AuthUser
from ..components.client.ui.terminal import Terminal
from ..model.message import MessageModel, MessageDestination, MessageRole, ServerMessageModel

_logger = logging.getLogger(__name__)


class SocketTCPClient(NetworkSocket):   # noqa
    SOCKET_TYPE: str = "tcp_client"

    def __init__(self, host: str, port: int, user_name: str | None = None, password: str | None = None):
        super().__init__(host, port)

        self.id: int | None = None
        self.user_name: str | None = user_name
        self.password: str | None = password
        self.credential: tuple[str, str] | None = None
        self.user_id: str | None = None

        self.state: str = objects.Client.PUBLIC
        self.server_session: str | None = None
        self._connected_to_server: bool = False  # currently connected to the server

        self.messages: queue.Queue[ServerMessageModel] = queue.Queue(maxsize=constants.SOCKET_MAX_MESSAGE_QUEUE_PER_WORKER)

        self.ui: Terminal = Terminal(self)  # TODO: make GUI type too depending on how we lunch the client!

    def __call__(self, *args, **kwargs):
        if not self.user_name:
            self.user_name = self.ui.input_username()
        self.credential = (self.user_name, self.password)
        self.login_info: objects.LoginInfo = {
            'id': self.id,
            'user_name': self.user_name,
            'password': self.password,
            'user_id': self.user_id
        }
        super().__call__(*args, **kwargs)

    def start(self):
        self.start_connecting_to_server()

        self.send_to_server(_c.make_message(_c.Codes.LOGIN, json.dumps(self.login_info)))

        AuthUser.login(self)
        time.sleep(1)  # Hold threads start here, avoid possibly receiving and sending login information from buffer

        # TODO: refactor this!
        t_receiver = threading.Thread(target=self.thread_receiver, daemon=True)
        t_broadcaster = threading.Thread(target=self.thread_broadcaster, daemon=True)
        t_sender = threading.Thread(target=self.thread_sender, daemon=True)

        t_receiver.start()
        t_broadcaster.start()
        t_sender.start()

        self.wait_or_die()  # keep main thread alive -

    def close_before(self):
        self.stop_connecting_to_server()
        self.stop_wait_forever()

    def start_connecting_to_server(self):
        self.ui.message_echo("Connecting to Server ...")
        self.connected_to_server = True

    def stop_connecting_to_server(self):
        self.ui.message_echo("Closing Server Connection ...")
        self.connected_to_server = False

    def thread_receiver(self):
        exception: BaseException | None = None
        while self.connected_to_server:
            try:
                message: ServerMessageModel = self.receive_message(self.socket)
                if not message:
                    break
                _logger.debug(message.body)
                self.messages.put(message)

            except KeyboardInterrupt as error:
                _logger.warning(f"(t_receiver) Interrupted by User, reason: {error}")
                exception = error
            except SystemExit as error:
                if error.code == _c.Codes.LOGOUT:
                    self.sys_error = error.code
                _logger.warning(f"(t_receiver) Interrupted by System, reason: {error}")
                exception = error
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                _logger.warning(f"(t_receiver) Network Connection error to the server, reason: {error}")
                exception = error
            finally:
                if exception:
                    self.stop_connecting_to_server()
        else:
            _logger.warning("(t_receiver) Exit naturally")
        self.stop_wait_forever()

    def thread_sender(self):
        exception: BaseException | None = None
        while self.connected_to_server:
            try:
                self.ui.next_command()
            except KeyboardInterrupt as error:
                _logger.warning(f"(t_sender) Interrupted by User, reason: {error}")
                exception = error
            except SystemExit as error:
                if error.code == _c.Codes.LOGOUT:
                    self.sys_error = error.code
                _logger.warning(f"(t_sender) Interrupted by System, reason: {error}")
                exception = error
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                _logger.warning(f"(t_sender) Network Connection error to the server, reason: {error}")
                exception = error
            finally:
                if exception:
                    self.stop_connecting_to_server()
        else:
            _logger.warning("(t_sender) Exit naturally")
        self.stop_wait_forever()

    def thread_broadcaster(self) -> None:
        while self.connected_to_server:
            message_to_broadcast: ServerMessageModel = self.messages.get()  # blocking - t_broadcaster
            self.broadcast(message_to_broadcast)
            self.messages.task_done()

    def broadcast(self, payload: ServerMessageModel) -> None:
        _display_type = _c.code_scan(payload.body)
        match _display_type:
            case _c.Codes.USER_LIST_ALL | _c.Codes.USER_LIST_LOGGED | _c.Codes.USER_LIST_UN_LOGGED:
                self.ui.display_users(_display_type, payload)
            case _c.Codes.GROUP_LIST:
                self.ui.display_groups(payload)
            case _c.Codes.CHANNEL_LIST_ALL | _c.Codes.CHANNEL_LIST_OWNED | _c.Codes.CHANNEL_LIST_JOINED | _c.Codes.CHANNEL_LIST_UN_JOINED:
                self.ui.display_channels(_display_type, payload)
            case _c.Codes.MESSAGE_LIST_SENT | _c.Codes.MESSAGE_LIST_RECEIVED | _c.Codes.MESSAGE_LIST_GROUP | _c.Codes.MESSAGE_LIST_CHANNEL:
                self.ui.display_messages(_display_type, payload)
            case _:
                self.ui.message_display(payload)

    def receive_message(self, connection: socket.socket, buffer_size: int = constants.SOCKET_STREAM_LENGTH) -> ServerMessageModel | None:
        message: str = self.receive(connection, buffer_size)
        if not message:
            return

        message: ServerMessageModel = ServerMessageModel.from_json(message)
        return message

    def send(self, message: str) -> int:  # noqa
        return super().send(self.socket, message)

    def send_message(self, message: MessageModel) -> int:   # noqa
        return self.send(message.to_json())

    def send_to_server(self, payload: str) -> None:
        sender = MessageDestination(self.id, self.user_name, role=MessageRole.USER)
        to = MessageDestination(self.server_session, "SERVER", role=MessageRole.SERVER)
        message = MessageModel.new_message(sender, to, payload)

        self.send_message(message)

    def send_to_all(self, payload: str) -> None:
        sender = MessageDestination(self.id, self.user_name, role=MessageRole.USER)
        to = MessageDestination(self.server_session, "SERVER", role=MessageRole.ALL)
        message = MessageModel.new_message(sender, to, payload)

        self.send_message(message)

    def send_to_group(self, group: str, payload: str) -> None:
        sender = MessageDestination(self.id, self.user_name, role=MessageRole.USER)
        to = MessageDestination(group, group, role=MessageRole.GROUP)
        message = MessageModel.new_message(sender, to, _c.make_message(_c.Codes.SEND_TO_GROUP, payload))

        self.send_message(message)

    def send_to_channel(self, channel: str, payload: str) -> None:
        sender = MessageDestination(self.id, self.user_name, role=MessageRole.USER)
        to = MessageDestination(channel, channel, role=MessageRole.CHANNEL)
        message = MessageModel.new_message(sender, to, _c.make_message(_c.Codes.SEND_TO_CHANNEL, payload))

        self.send_message(message)

    def send_to_user(self, user: str, payload: str) -> None:
        sender = MessageDestination(self.id, self.user_name, role=MessageRole.USER)
        to = MessageDestination(user, user, role=MessageRole.USER)
        message = MessageModel.new_message(sender, to, _c.make_message(_c.Codes.SEND_TO_USER, payload))

        self.send_message(message)

    # ------------------------------------
    # Getter and setters
    # ------------------------------------

    @property
    def connected_to_server(self) -> bool:
        return self._connected_to_server  # pragma: no cover

    @connected_to_server.getter
    def connected_to_server(self) -> bool:
        return self._connected_to_server

    @connected_to_server.setter
    def connected_to_server(self, value: bool) -> None:
        if not isinstance(value, (bool, int)):
            raise TypeError(f"Value for connected_to_server must be of type (bool, int), {type(value)} passed")
        self._connected_to_server = value
