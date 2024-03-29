import sys
import logging
import socket
import threading
from types import MappingProxyType

from . import constants
from . import settings
from . import logger


def run(argv: tuple[str, ...] = tuple(), cli: bool = True) -> None:  # noqa:C901
    # TODO: use better cli lib
    # TODO: make a default / fallback logger in case we fail to load the app logger!
    if not cli:
        tcp_app_type, _host, _port = ("tcp_server", "localIpAddr", "20020")
    else:
        if len(argv) < 3:
            # print(usage) TODO Add usage
            sys.exit(0)
        tcp_app_type, _host, _port = argv[:3]

    env_file = f".{tcp_app_type}.env"
    conf: MappingProxyType = settings.configure(env_file)

    logger.ColoredFormatter.init(conf.get("BACKEND_LOG_CONF_NAME", constants.LOG_CONF_NAME_DEFAULT), tcp_app_type)
    _logger = logging.getLogger(__name__)  # Must Create logger here, as it needs to be initialized

    # Import here anything that uses the logger
    from .core import NetworkSocket
    from .core import SocketTCPClient
    from .core import SocketTCPServer
    from chatbox.app.constants import chat_internal_codes as _c

    app_supported = NetworkSocket.SOCKET_TYPES
    if tcp_app_type not in app_supported:
        _logger.error(f"Supported TCP app {app_supported}, got instead: {tcp_app_type}")
        sys.exit(1)

    host: str = NetworkSocket.get_app_host(_host)
    port: int = NetworkSocket.get_app_port(_port)
    _logger.info("Launching %s app, this may take few milliseconds ....", tcp_app_type)

    stop = True
    while True:
        if tcp_app_type == app_supported[0]:  # TODO: improve this
            app = SocketTCPServer(host, port)
        elif tcp_app_type == app_supported[1]:

            user = None
            password = None
            for a in argv:
                if a.startswith('--user'):
                    user = a.replace('--user=', '')
                elif a.startswith('--password'):
                    password = a.replace('--password=', '')
            app = SocketTCPClient(host, port, user, password)
        else:
            _logger.error(f"Supported TCP app {app_supported}, got instead: {tcp_app_type}")  # we check this above, but double check for user errors
            sys.exit(1)

        out_message: str = f"{app} :: "
        log_level: int = logging.INFO
        exit_code: int = 0
        exception: BaseException | None = None
        try:
            app()
        except KeyboardInterrupt:
            out_message += "[APP_EXIT_K_INTERRUPT] - Interrupted by signal 2: SIGINT"
            log_level = logging.WARNING
            exit_code = 130
        except SystemExit as exit_error:
            if exit_error.code == _c.Codes.LOGOUT:
                stop = False
            out_message += "[APP_EXIT_SYSTEM] - Interrupted by System"
            log_level = logging.WARNING
            exit_code = 130
        except (RuntimeError, SyntaxError, TypeError, ValueError, LookupError) as programming_error:
            out_message += "[APP_PROG_ERROR] - App Error"
            exception = programming_error
            log_level = logging.ERROR
            exit_code = 1
        except socket.timeout as socket_timeout:
            out_message += "[APP_SOCKET_TIMEOUT] - Socket Timed out"
            exception = socket_timeout
            log_level = logging.ERROR
            exit_code = 1

        except BlockingIOError as blocking_io_error:
            out_message += "[APP_I/O_ERROR_BLOCKING] - Unexpected Blocking occurred"
            exception = blocking_io_error
            log_level = logging.ERROR
            exit_code = 1

        except (BrokenPipeError, ConnectionAbortedError, ConnectionRefusedError, ConnectionError) as connection_error:
            out_message += "[APP_I/O_ERROR_CONNECTION] - Connection error"
            exception = connection_error
            log_level = logging.ERROR
            exit_code = 1
        except (OSError, IOError, socket.error) as io_error:
            out_message += "[APP_I/O_ERROR_GENERIC] - Something went wrong with the Connection"
            exception = io_error
            log_level = logging.ERROR
            exit_code = 1

        except threading.ThreadError as thread_error:
            out_message += "[APP_THREAD_ERROR] - "
            exception = thread_error
            log_level = logging.ERROR
            exit_code = 1

        except Exception as main_exception:
            out_message += "[APP_EXCEPTION] - Something went wrong"
            exception = main_exception
            log_level = logging.CRITICAL
            exit_code = 1
        except (StopIteration, GeneratorExit) as iter_error:
            out_message += "[APP_EXIT_ERROR] - "
            exception = iter_error
            log_level = logging.ERROR
            exit_code = 1

        except BaseException as base_exception:
            out_message += "[APP_BASE_EXCEPTION] - Something went wrong"
            exception = base_exception
            log_level = logging.CRITICAL
            exit_code = 1
        else:
            out_message += "[APP_EXIT_NO_ERRORS] - Process Terminated with no errors."
            log_level = logging.INFO
            exit_code = 0

        finally:
            out_message += "; Closing ..."
            if exception:
                _logger.log(log_level, out_message)
                _logger.exception(f"Exception at app {tcp_app_type} launcher at host={host}, port={port} {app}, reason = {exception}", exc_info=exception)
            else:
                out_message += " with no errors... "
                _logger.log(log_level, out_message)
            if not stop:
                stop = True
                continue
            sys.exit(exit_code)
