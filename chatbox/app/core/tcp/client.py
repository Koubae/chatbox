import json
import logging
import sys
import threading
from typing import Type

from .network_socket import NetworkSocket

from chatbox.app.constants import chat_internal_codes as codes
from . import objects

_logger = logging.getLogger(__name__)


class SocketTCPClient(NetworkSocket):   # noqa
    SOCKET_TYPE: str = "tcp_client"

    def __init__(self, host: str, port: int, user_name: str|None = None, password: str|None = None):
        super().__init__(host, port)

        self.user_name: str|None = user_name
        self.password: str|None = password
        self.credential: tuple[str, str]|None = None
        self.user_id: str|None = None

        self.state: str = objects.Client.PUBLIC
        self.server_session: str | None = None
        self._connected_to_server: bool = False # currently connected to the server

    def __call__(self, *args, **kwargs):
        if not self.user_name:
            self.user_name = self._request_user_name()
        if not self.password:
            self.password = self._request_password()
        self.credential = (self.user_name, self.password)
        self.login_info: objects.LoginInfo = {
            'user_name': self.user_name,
            'password': self.password,
            'user_id': self.user_id
        }
        super().__call__(*args, **kwargs)


    def start(self):
        exception_to_raise: list[Type[BaseException], ...] = [
            KeyboardInterrupt,
            KeyboardInterrupt,
            ConnectionResetError,
            ConnectionRefusedError,
            ConnectionAbortedError,
            ConnectionError
        ]
        exception: BaseException | None = None
        self.start_connecting_to_server()

        self.send(codes.make_message(codes.LOGIN, json.dumps(self.login_info)))
        # TODO: Improve printing
        # TODO: check that, once password is saved in server side, this will work!
        print("Identification Required")
        while self.state != objects.Client.LOGGED:
            message: str = self.receive(self.socket)
            if not message:
                raise ConnectionResetError("Server closed connection before could login")

            if codes.code_in(codes.LOGIN_SUCCESS, message):
                self.server_session = codes.get_message(codes.LOGIN_SUCCESS, message)
                self.state = objects.Client.LOGGED
                break
            elif codes.code_in(codes.IDENTIFICATION_REQUIRED, message):
                if not self.user_id:
                    self.user_id = codes.get_message(codes.IDENTIFICATION_REQUIRED, message)
                    self.login_info['user_id'] = self.user_id
                    _logger.info(f">>> client token is {self.user_id}")
                else:
                    print("Authentication failed")

            self.login_info['password'] = self._request_password()
            self.send(codes.make_message(codes.IDENTIFICATION, json.dumps(self.login_info)))
        # TODO: refactor this!
        # client is not logged in, let's spawn 1 thread for seanding and receiving
        t_receiver = threading.Thread(target=self.thread_receiver, daemon=True)
        t_sender = threading.Thread(target=self.thread_sender, daemon=True)

        # start threads
        t_receiver.start()
        t_sender.start()

        t_receiver.join()
        t_sender.join()

        try:
            self.wait_or_die()  # keep main thread alive -
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
                _logger.warning(
                    f"Exception of type {error.__class__} no inside exception_to_raise, adding it programmatically")
                exception_to_raise.append(error.__class__)
        finally:
            if exception and exception.__class__ in exception_to_raise:
                self.stop_connecting_to_server()
                self.stop_wait_forever()
                raise exception from None

        self.stop_connecting_to_server()
        self.stop_wait_forever()

    def close_before(self):
        self.stop_connecting_to_server()
        self.stop_wait_forever()

    def thread_receiver(self):
        exception: BaseException | None = None
        while self.connected_to_server:
            try:
                message: str = self.receive(self.socket)
                if not message:
                    break
                _logger.debug(message)
                print(message)
            except KeyboardInterrupt as error:
                _logger.warning(f"(t_receiver) Interrupted by User, reason: {error}")
                exception = error
            except SystemExit as error:
                _logger.warning(f"(t_receiver) Interrupted by System, reason: {error}")
                exception = error
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                _logger.warning(f"(t_receiver) Network Connection error to the server, reason: {error}")
                exception = error
            finally:
                if exception:
                    self.stop_connecting_to_server()
        else:
            _logger.warning(f"(t_receiver) Exit naturally")
        self.stop_wait_forever()

    def thread_sender(self):
        exception: BaseException | None = None
        while self.connected_to_server:
            try:
                message: str = self._request_message()
                self.send(message)
            except KeyboardInterrupt as error:
                _logger.warning(f"(t_sender) Interrupted by User, reason: {error}")
                exception = error
            except SystemExit as error:
                _logger.warning(f"(t_sender) Interrupted by System, reason: {error}")
                exception = error
            except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as error:
                _logger.warning(f"(t_sender) Network Connection error to the server, reason: {error}")
                exception = error
            finally:
                if exception:
                    self.stop_connecting_to_server()
        else:
            _logger.warning(f"(t_sender) Exit naturally")
        self.stop_wait_forever()

    def start_connecting_to_server(self):
        print("Connecting to Server ...")
        self.connected_to_server = True

    def stop_connecting_to_server(self):
        print("Closing Server Connection ...")
        self.connected_to_server = False

    def send(self, message: str) -> int:  # noqa
        return super().send(self.socket, message)

    def _request_message(self) -> str:     # pragma: no cover
        return input()

    def _request_user_name(self) -> str:   # pragma: no cover
        user_name = input(">>> Enter user name: ")
        return user_name

    def _request_password(self) -> str:    # pragma: no cover
        password = input(">>> Enter Password: ")
        return password

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