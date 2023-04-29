import json
import sys
import socket
import threading
import logging

from chatbox.app import constants
from .objects import Address


_logger = logging.getLogger(__name__)


class NetworkSocketException(Exception):
    pass


class NetworkSocket:
    SOCKET_TYPES: tuple[str, ...] = ("tcp_server", "tcp_client")
    SOCKET_TYPE: str = "tcp_socket_abstract"
    socket_options: list[tuple[int, int, int]] = [
        #: SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1),

        #: @see https://stackoverflow.com/a/31827588/13903942
        #: Disable Nagle's algorithm by default.
        #: ``[(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)]``
        (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
        (socket.IPPROTO_TCP, socket.TCP_CORK, 1),  # TCP_CORK  Only available in linux.

    ]

    socket_options_keep_alive: list[tuple[int, int, int]] = [
        (socket.SOL_TCP, socket.TCP_KEEPCNT, constants.SOCKET_MAX_TCP_KEEPCNT),
        (socket.SOL_TCP, socket.TCP_KEEPIDLE, 1),
        (socket.SOL_TCP, socket.TCP_KEEPINTVL, 1),
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    ]

    def __init__(self, host: str, port: int):
        self.address: Address = Address(host, port)
        self.socket: socket.socket = self.socket_on()

        self.name: str = f"{socket.gethostname()}@<{self.address}>"
        self.socket_ready: threading.Event = threading.Event()         # socket is ready to operate
        self.socket_connected: threading.Event = threading.Event()     # socket is connected (sock.bind or sock.connect)
        self.socket_closed: threading.Event = threading.Event()        # socket is closed
        self.socket_wait_forever: threading.Event = threading.Event()  # socket is waiting forever.

    def __del__(self):
        self.terminate()

    def __str__(self):
        return f"{self.__class__.__name__}::{self.SOCKET_TYPE} {self.name or f'@<{self.address}>'}"

    def __repr__(self):
        return f"{self.__class__.__name__}(socket_type={self.SOCKET_TYPE}, address={self.address})"

    def __call__(self, *args, **kwargs):
        connected: bool = self.socket_connect()
        if not connected:
            raise NetworkSocketException(f"Something went wrong while connecting to {self.address}")
        self._start()

    # --------------------------------------------------
    # Socket API
    # --------------------------------------------------
    # noinspection PyMethodMayBeStatic
    def socket_on_before(self):
        return NotImplemented

    # noinspection PyMethodMayBeStatic
    def socket_on_after(self, _socket: socket.socket):
        return NotImplemented

    def socket_on(self):
        self.socket_on_before()
        _socket: socket.socket = NetworkSocket.create_tcp_socket(self.socket_options)
        self.socket_on_after(_socket)
        return _socket

    def socket_connect(self) -> bool:
        try:
            if self.SOCKET_TYPE == "tcp_server":
                self.socket.bind(tuple(self.address))
                self.socket.listen(constants.SOCKET_MAX_CONNECTIONS)
            elif self.SOCKET_TYPE == "tcp_client":
                self.socket.connect(tuple(self.address))
            else:
                _logger.warning(f"{self} - is an abstract TCP Socket and does not implement a connection method, use a implemented one!")
                return False
        except (ConnectionRefusedError, ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError, ConnectionError) as error:
            _logger.exception("%s - Error while establishing connection to %s, reason : %s", self, self.address, error, exc_info=error)
            return False
        else:
            self.socket_connected.set()
            self.socket_ready.set()
            _logger.info("%s Connected to %s", self, self.address)
            return True

    def _start(self):
        self.start_before()

        out_message: str = ""
        log_level: int = logging.INFO
        exit_code: int = 0
        exception: BaseException | None = None

        try:
            self.start()
            self.start_after()
        except (RuntimeError, SyntaxError, TypeError, ValueError, LookupError) as programming_error:
            out_message = "[PROG_ERROR] - App Error"
            exception = programming_error
            log_level = logging.ERROR
            exit_code = 1
        except socket.timeout as socket_timeout:
            out_message = "[SOCKET_TIMEOUT] - Socket Timed out"
            exception = socket_timeout
            log_level = logging.ERROR
            exit_code = 1

        except BlockingIOError as blocking_io_error:
            out_message = "[I/O_ERROR_BLOCKING] - Unexpected Blocking occurred"
            exception = blocking_io_error
            log_level = logging.ERROR
            exit_code = 1

        except (BrokenPipeError, ConnectionAbortedError, ConnectionRefusedError, ConnectionError) as connection_error:
            out_message = "[I/O_ERROR_CONNECTION] - Connection error"
            exception = connection_error
            log_level = logging.ERROR
            exit_code = 1
        except (OSError, IOError, socket.error) as io_error:
            out_message = "[I/O_ERROR_GENERIC] - Something went wrong with the Connection"
            exception = io_error
            log_level = logging.ERROR
            exit_code = 1

        except threading.ThreadError as thread_error:
            out_message = "[THREAD_ERROR] - "
            exception = thread_error
            log_level = logging.ERROR
            exit_code = 1

        except Exception as main_exception:
            out_message = "[EXCEPTION] - Something went wrong"
            exception = main_exception
            log_level = logging.CRITICAL
            exit_code = 1
        except (StopIteration, GeneratorExit) as iter_error:
            out_message = "[EXIT_ERROR] - "
            exception = iter_error
            log_level = logging.ERROR
            exit_code = 1

        except BaseException as base_exception:
            out_message = "[BASE_EXCEPTION] - Something went wrong"
            exception = base_exception
            log_level = logging.CRITICAL
            exit_code = 1
        else:
            out_message = "[EXIT_NO_ERRORS] - Process Terminated with no errors."
            log_level = logging.INFO
            exit_code = 0

        finally:
            out_message = f"{self} - {out_message}; Closing ..."
            if exception:
                out_message = f"""{self} - {out_message};
- Error: {exception.__class__.__name__} reason => {exception}
Stack Trace:

                """.lstrip()
                _logger.exception(out_message, exc_info=exception)
            else:
                _logger.log(log_level, out_message)

            try:
                self.terminate()
            except BaseException as error:
                _logger.exception(f"{self} - Error While closing the main socket, reason: {error}", exc_info=error)
            finally:
                if constants.KILL_APP_AT_SOCKET_TERMINATE:
                    sys.exit(exit_code)

    # noinspection PyMethodMayBeStatic
    def start_before(self):
        return NotImplemented

    # noinspection PyMethodMayBeStatic
    def start_after(self):
        return NotImplemented

    # noinspection PyMethodMayBeStatic
    def start(self):
        return NotImplemented

    def terminate(self):
        self._close()

    def _close(self):
        self.close_before()
        self.close()
        self.close_after()

    # noinspection PyMethodMayBeStatic
    def close_before(self):
        return NotImplemented

    # noinspection PyMethodMayBeStatic
    def close_after(self):
        return NotImplemented

    def close(self):
        if not self.socket or not isinstance(self.socket, socket.socket):
            _logger.debug(f"{self} - Try to close on Socket but instance doesn't have a socket!")
            return
        elif not isinstance(self.socket, socket.socket):
            _logger.warning(f"{self} - Try to close on Socket but is not an object of type socket.socket, type: {type(self.socket)}")
            return

        _logger.info(f"{self} - Shutting down and then closing Socket")
        if self.socket_connected.is_set():
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                _logger.info(f"{self} - Socket Shutdown for READ and WRITE  with no errors.")
            except OSError as error:  # Is it errors out probably it's already shutdown. No need further actions
                _logger.warning(f"{self} - Encountered an error while Shutting Down, error : %s", error)
            finally:
                self.socket_connected.clear()

        if self.socket_closed.is_set():
            _logger.info(f"{self} - Socket is already closed!")
            return

        try:
            self.socket.close()
            _logger.info(f"{self} - Socket Closed successfully.")
        except OSError as error:
            _logger.warning(f"{self} - Encountered an error while closing socket, error : %s", error)
        finally:
            self.socket_closed.set()
            self.socket_ready.clear()

    def stop_wait_forever(self):
        self.socket_wait_forever.set()

    def start_wait_forever(self):
        self.socket_wait_forever.clear()
        self.wait_or_die()

    def wait_or_die(self):
        """Let a tcp socket wait indefinitely, useful especially for client connections"""
        exception: Exception | None = None
        try:
            self.socket_wait_forever.wait()  # blocking. waits till threading.Event is triggered
        except (KeyboardInterrupt, SystemExit, ConnectionError):
            pass
        except Exception as error:
            exception = error
        finally:
            if exception:
                raise exception from None

    # ······························
    # Socket BroadCasting
    # ······························
    def receive(self, connection: socket.socket, buffer_size: int = constants.SOCKET_STREAM_LENGTH) -> str | None:
        try:
            message: bytes = connection.recv(buffer_size)
        except socket.error as error:
            _logger.exception(f"{self} - Socket error on receive handler, reason: {error}", exc_info=error)
        except Exception as error:
            _logger.exception(f"{self} - Exception error on receive handler, reason: {error}", exc_info=error)
        else:
            if not message:
                return None
            return self.decode_message(message)

    def send(self, connection: socket.socket, message: str) -> int:
        try:
            total_sent = connection.send(self.encode_message(message))
        except socket.error as error:
            _logger.exception(f"{self} - Socket error on send handler, reason: {error}", exc_info=error)
            total_sent = -1
        except Exception as error:
            _logger.exception(f"{self} - Exception error on send handler, reason: {error}", exc_info=error)
            total_sent = -1

        return total_sent

    # ^^^^^^^^^ NotImplemented Methods ^^^^^^^^^
    def broadcast(self, client_identifier: int, message: str, send_all: bool = False) -> None:
        raise NotImplementedError("Method not implemented!")

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------
    @staticmethod
    def get_app_host(host: str) -> str:
        if host == constants.SOCKET_HOST_DEFAULT:
            return NetworkSocket.get_local_ipaddr()
        return host

    @staticmethod
    def get_app_port(port: str) -> int:
        try:
            port = int(port)
        except (ValueError, AttributeError):
            port = constants.SOCKET_PORT_DEFAULT
        return port

    @staticmethod
    def get_local_ipaddr() -> str:
        """Get the default IP Address of the host machine"""
        return socket.gethostbyname(socket.gethostname())

    @staticmethod
    def create_tcp_socket(socket_options:  list[tuple[int, int, int]] = None) -> socket.socket:
        """Creates a simple TCP Socket"""
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_options = socket_options or []
        for opt in socket_options:
            socket_connection.setsockopt(*opt)

        return socket_connection

    @staticmethod
    def encode_message(message: str) -> bytes:
        return message.encode(constants.ENCODING)

    @staticmethod
    def decode_message(message: bytes) -> str:
        return message.decode(constants.ENCODING)

    @staticmethod
    def parse_json(message: str) -> dict | None:
        try:
            loaded = json.loads(message)
        except json.JSONDecodeError as error:
            _logger.exception(f'Error while parsing json ({message[:255]}), reason {error}', exc_info=error)
            return None
        else:
            return loaded
