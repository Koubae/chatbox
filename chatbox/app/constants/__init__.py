import os


# --------------------
# App
# --------------------
APP_NAME: str = "ChatBox-Master"

# ...... SOCKET ......
SOCKET_HOST_DEFAULT: str = "localIpAddr"
SOCKET_PORT_DEFAULT: int = 10_000
SOCKET_MAX_CONNECTIONS: int = 5
SOCKET_MAX_TCP_KEEPCNT: int = 127


# --------------------
# Configurations
# --------------------
ENV_CONF_NAME : str = ".tcp_server.env"
LOG_CONF_NAME : str = "logger.server.conf"
LOG_CONF_NAME_DEFAULT : str = "logger.conf"

# --------------------
# Directories
# --------------------
DIR_ROOT: str = os.path.dirname(os.path.abspath(__file__)).replace('/constants', '').replace('/app', '')
DIR_APP = os.path.join(DIR_ROOT, "app")
DIR_STORAGE = os.path.join(DIR_APP, "storage")
DIR_LOGS = os.path.join(DIR_STORAGE, "logs")
DIR_CRASHES = os.path.join(DIR_LOGS, "crashes")

DIR_CONFIG: str = os.path.join(DIR_ROOT, "../config")
CONFIG_DIRECTORY_RELATIVE_APP: str = "../../../config"