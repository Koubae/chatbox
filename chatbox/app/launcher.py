import sys
import logging
from types import MappingProxyType

from . import usage
from . import settings
from . import logger

from .core import SocketClient
from .core import SocketServer


def run(argv: tuple[str, ...] = tuple(), cli: bool = True) -> None:
    # TODO: use better cli lib
    # TODO: make a default / fallback logger in case we fail to load the app logger!
    if not cli:
        tcp_app, host, port =  ("server", "localIpAddr", "20020")
    else:
        if len(argv) < 3:
            # print(usage)
            sys.exit(0)
        tcp_app, host, port = argv

    app_supported =  ("server", "client")
    if tcp_app not in app_supported:
        print(f"Supported TCP app {app_supported}, got {tcp_app}")

    env_file = ".server.env" if tcp_app == 'server' else ".client.env"
    conf: MappingProxyType = settings.configure(env_file)

    logger.ColoredFormatter.init(conf["BACKEND_LOG_CONF_NAME"])
    _logger = logging.getLogger(__name__)
    _logger.info("Launhced")
