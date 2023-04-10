import json
import sys
import socket
import threading
import logging
import time

from chatbox.app import constants
from .objects import Address


_logger = logging.getLogger(__name__)


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
        (socket.IPPROTO_TCP, socket.TCP_CORK, 1), # TCP_CORK  Only available in linux. TODO: check for other OS

    ]

    socket_options_keep_alive: list[tuple[int, int, int]]  = [
        (socket.SOL_TCP, socket.TCP_KEEPCNT, constants.SOCKET_MAX_TCP_KEEPCNT),
        (socket.SOL_TCP, socket.TCP_KEEPIDLE, 1),
        (socket.SOL_TCP, socket.TCP_KEEPINTVL, 1),
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    ]

    def __init__(self, host: str, port: int):
        self.address: Address = Address(host, port)
        self.socket: socket.socket = self.socket_on()

        self.name: str = f"{socket.gethostname()}@<{self.address}>"
        self.socket_ready: bool = False        # socket is ready to operate  # TODO: Make setter for these flags value! (USe bitwise as well?)TODO: Semaphore or signal?
        self.socket_connected: bool = False    # socket is connected (bind to address when server or connected to address when client) # TODO: Semaphore or signal?
        self.socket_closed: bool = False       # socket is closed # TODO: Semaphore or signal?
        self.socket_wait_forever: bool = False # socket is waiting forever.  # TODO: Semaphore or signal?

    def __del__(self):
        self.terminate()

    def __str__(self):
        return f"{self.__class__.__name__}::{self.SOCKET_TYPE} <{self.address}>"
    def __repr__(self):
        return f"{self.__class__.__name__}(socket_type={self.SOCKET_TYPE}, address={self.address})"

    def __call__(self, *args, **kwargs):
        connected: bool = self.socket_connect()
        if not connected:
            # TODO Implement Errror ????
            raise Exception(f"Something went wrong while connecting to {self.address}")
        self._start()

    # --------------------------------------------------
    # Socket API
    # --------------------------------------------------
    def socket_on_before(self):  #: @override Hook
        return NotImplemented

    def socket_on_after(self, _socket: socket.socket): #: @override Hook
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
                _logger.warning(f"{self.name} is an abstract TCP Socket and does not implement a connection method, use a implemented one!")
                return False
        except (ConnectionRefusedError, ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError, ConnectionError) as error:
            _logger.exception("Error while establishing connection to %s, reason : %s", self.address, error, exc_info=error)
            return False
        else:
            self.socket_connected = True
            self.socket_ready = True
            _logger.info("%s Connected to %s", self, self.address)
            return True

    def _start(self):
        self.start_before()

        out_message: str = ""
        log_level: int = logging.INFO
        exit_code: int = 0
        exception: BaseException|None = None

        try:
            self.start()
            self.start_after()  # TODO: not sure if is 'after it finishih running' or 'after is started and is running' , if second option then this should run in a separate thread or be just a coroutine

        except KeyboardInterrupt as _:
            out_message = f"[EXIT_K_INTERRUPT] - Interrupted by signal 2: SIGINT"
            log_level = logging.WARNING
            exit_code = 130
        except SystemExit as _:
            out_message = f"[EXIT_SYSTEM] - Interrupted by System"
            log_level = logging.WARNING
            exit_code = 130
        except (RuntimeError, SyntaxError, TypeError, ValueError, LookupError) as programming_error:
            out_message = f"[PROG_ERROR] - App Error"
            exception = programming_error
            log_level = logging.ERROR
            exit_code = 1
        except socket.timeout as socket_timeout:
            out_message = f"[SOCKET_TIMEOUT] - Socket Timed out"
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
            out_message =  "[I/O_ERROR_GENERIC] - Something went wrong with the Connection"
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
            out_message += "; Closing ..."
            if exception:
                out_message = f"{out_message}; Error: {exception.__class__.__name__} error stack trace will log shortly, reason => {exception}\n"
                _logger.log(log_level, out_message)
                _logger.exception(f"Stack Trace of {exception}:\n\n", exc_info=exception)
            else:
                _logger.log(log_level, out_message)

            try:
                self.terminate()
            except BaseException as error:
                _logger.exception(f"Error While closing the main socket, reason: {error}", exc_info=error)
            finally:
                if constants.KILL_APP_AT_SOCKET_TERMINATE:
                    sys.exit(exit_code)

    def start_before(self): #: @override Hook
        return NotImplemented

    def start_after(self):   #: @override Hook
        return NotImplemented

    def start(self):          #: @override Hook
        return NotImplemented

    def terminate(self):
        self._close()

    def _close(self):
        self.close_before()
        self.close()
        self.close_after()

    def close_before(self): #: @override Hook
        return NotImplemented

    def close_after(self):  #: @override Hook
        return NotImplemented

    def close(self):
        if not self.socket or not isinstance(self.socket, socket.socket):
            _logger.debug(f"Try to close on Socket {self.name} but is not an object of type socket.socket, type: {type(self.socket)}")
            return

        _logger.info(f"{self.name} - Closing Socket")
        if self.socket_connected:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                _logger.info(f"{self.name} - Socket Shutdown for READ and WRITE  with no errors.")
            except OSError as error: # Is it errors out probably it's already shutdown. No need further actions
                _logger.warning(f"Socket {self.name} encountered an error while Shutting Down, error : %s", error)
            finally:
                self.socket_connected = False

        if self.socket_closed:
            _logger.debug(f"Socket {self.name} is already closed!")
            return

        try:
            self.socket.close()
            _logger.info(f"{self.name} - Socket Closed without errors.")
        except OSError as error:
            _logger.warning(f"Socket {self.name} encountered an error while closing socket, error : %s", error)
        finally:
            self.socket_closed = True

    def stop_wait_forever(self):
        self.socket_wait_forever = False

    def start_wait_forever(self):
        self.socket_wait_forever = True
        self.wait_or_die()

    def wait_or_die(self):
        """Let a tcp socket wait indefinitely, useful especially for client connections"""
        while self.socket_wait_forever:  # TODO: use other way to do this, for instance some Semaphore, Signals or stuff like this
            time.sleep(1)
        else:
            self._close()

    # ······························
    # Socket BroadCasting
    # ······························
    def receive(self, connection: socket.socket, buffer_size: int = constants.SOCKET_STREAM_LENGTH) -> str|None:
        try:
            message: bytes = connection.recv(buffer_size)
        except socket.error as error:
            _logger.exception(f"Error receiving socket error, reason: {error}", exc_info=error)
        except Exception as error:
            _logger.exception(f"Error receiving Exception error, reason: {error}", exc_info=error)
        else:
            if not message:
                return None
            return self.decode_message(message)

    def send(self, connection: socket.socket, message: str) -> int:
        try:
            total_sent = connection.send(self.encode_message(message))
        except socket.error as error:
            _logger.exception(f"Error sending socket error, reason: {error}", exc_info=error)
            total_sent = -1
        except Exception as error:
            _logger.exception(f"Error sending Exception error, reason: {error}", exc_info=error)
            total_sent = -1

        return total_sent

    # ^^^^^^^^^ NotImplemented Methods ^^^^^^^^^
    def broadcast(self, client_identifier: int, message: str) -> None:
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
        except (ValueError, AttributeError) as _:
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
    def parse_json(message: str) -> dict|None:
        try:
            loaded = json.loads(message)
        except json.JSONDecodeError as error:
            _logger.exception(f'Error while parsing json, reason {error}', exc_info=error)
            return None
        else:
            return loaded
