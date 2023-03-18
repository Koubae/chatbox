import sys
import logging
from types import MappingProxyType

from . import constants
from . import usage
from . import settings
from . import logger

from .core import NetworkSocket
from .core import SocketTCPClient
from .core import SocketTCPServer


def run(argv: tuple[str, ...] = tuple(), cli: bool = True) -> None:
    # TODO: use better cli lib
    # TODO: make a default / fallback logger in case we fail to load the app logger!
    if not cli:
        tcp_app_type, _host, _port =  ("tcp_server", "localIpAddr", "20020")
    else:
        if len(argv) < 3:
            # print(usage)
            sys.exit(0)
        tcp_app_type, _host, _port = argv

    env_file =  f".{tcp_app_type}.env"
    conf: MappingProxyType = settings.configure(env_file)

    logger.ColoredFormatter.init(conf.get("BACKEND_LOG_CONF_NAME", constants.LOG_CONF_NAME_DEFAULT), tcp_app_type)
    _logger = logging.getLogger(__name__) # Must Create logger here, as it needs to be initialized

    app_supported =  NetworkSocket.SOCKET_TYPES
    if tcp_app_type not in app_supported:
        _logger.error(f"Supported TCP app {app_supported}, got instead: {tcp_app_type}")
        sys.exit(1)

    host: str = NetworkSocket.get_app_host(_host)
    port: int = NetworkSocket.get_app_port(_port)
    _logger.info("Launching %s app, this may take few milliseconds ....", tcp_app_type)

    if tcp_app_type == app_supported[0]: # TODO: improve this
        app = SocketTCPServer(host, port)
    elif tcp_app_type == app_supported[1]:
        app = SocketTCPClient(host, port)
    else:
        _logger.error(f"Supported TCP app {app_supported}, got instead: {tcp_app_type}") # we check this above, but double check for user errors
        sys.exit(1)

    _logger.info(app)
