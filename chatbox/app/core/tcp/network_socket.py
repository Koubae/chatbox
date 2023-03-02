import sys
import socket
import threading
import logging
import time

from chatbox.app import constants
from .objects import Address


MAX_TCP_KEEPCNT = 127
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
        (socket.SOL_TCP, socket.TCP_KEEPCNT, MAX_TCP_KEEPCNT),
        (socket.SOL_TCP, socket.TCP_KEEPIDLE, 1),
        (socket.SOL_TCP, socket.TCP_KEEPINTVL, 1),
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    ]

    def __init__(self, host: str, port: int):
        self.address: Address = Address(host, port)
        self.socket: socket.socket = self.socket_on()


    def __str__(self):
        return f"{self.__class__.__name__}::{self.SOCKET_TYPE} <{self.address}>"
    def __repr__(self):
        return f"{self.__class__.__name__}(socket_type={self.SOCKET_TYPE}, address={self.address})"

    def __call__(self, *args, **kwargs):

        self._start()

    # --------------------------------------------------
    # Socket API
    # --------------------------------------------------
    def socket_on_before(self): ...  #: @override Hook
    def socket_on_after(self, _socket: socket.socket): ...  #: @override Hook
    def socket_on(self):
        self.socket_on_before()
        _socket: socket.socket = NetworkSocket.create_tcp_socket(self.address, self.SOCKET_TYPE, self.socket_options)
        self.socket_on_after(_socket)
        return _socket

    def _start(self):
        self.start_before()

        out_message: str = ""
        log_level: int = logging.INFO
        exit_code: int = 0
        exception: BaseException|None = None

        try:
            self.start()
            self.start_after()

        except KeyboardInterrupt as _:
            out_message = f"[EXIT_K_INTERRUPT] - Interrupted by signal 2: SIGINT"
            log_level = logging.WARNING
            exit_code = 130
        except SystemExit as _:
            out_message = f"[EXIT_SYSTEM] - Interrupted by System"
            log_level = logging.WARNING
            exit_code = 130
        except (RuntimeError, SyntaxError, TypeError, ValueError, LookupError, RuntimeError) as programming_error:
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
                self._close()
            except BaseException as error:
                _logger.exception(f"Error While closing the main socket, reason: {error}", exc_info=error)
            finally:
                sys.exit(exit_code)


    def start_before(self): ...  #: @override Hook
    def start_after(self): ...   #: @override Hook
    def start(self): ...         #: @override Hook


    def _close(self):
        self.close_before()
        self.close()
        self.close_after()

    def close_before(self): ... #: @override Hook
    def close_after(self): ...  #: @override Hook
    def close(self): ...  #: @override Hook


    def wait_or_die(self):
        """Let a tcp socket wait indefinitely, useful especially for client connections"""
        while self.socket_on:  # TODO: use other way to do this, for instance some Semaphore, Signals or stuff like this
            time.sleep(1)
        else:
            self._close()

    # ······························
    # NotImplemented Methods
    # ······························
    def broadcast(self, message: str) -> None:
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
    def create_tcp_socket(address: Address, server_type: str = "tcp_server", socket_options:  list[tuple[int, int, int]] = None) -> socket.socket:
        """Creates a simple TCP Socket"""
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if server_type == "tcp_client":
            socket_connection.connect(tuple(address))
        else:
            socket_connection.bind(tuple(address))

        socket_options = socket_options or []
        for opt in socket_options:
            socket_connection.setsockopt(*opt)

        return socket_connection
