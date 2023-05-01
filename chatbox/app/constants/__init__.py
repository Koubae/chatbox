import os

# --------------------
# MISC
# --------------------
SECONDS: int = 1
MINUTES: int = SECONDS * 60
HOUR: int = MINUTES * 60
DAY: int = HOUR * 24

# --------------------
# App
# --------------------
APP_NAME: str = "ChatBox-Master"

CLI_NEXT_INPUT: str = ">>> "

SERVER_SESSION_TIME_SECONDS: int = HOUR
KILL_APP_AT_SOCKET_TERMINATE: bool = False  # if the socket app (client or server) is terminated, run sys.exit else skip
ENCODING: str = "UTF-8"
DATETIME_DEFAULT: str = "%Y-%m-%d %H:%M:%S"

# ...... SOCKET ......
SOCKET_HOST_DEFAULT: str = "localIpAddr"
SOCKET_PORT_DEFAULT: int = 10_000
SOCKET_MAX_CONNECTIONS: int = 5
SOCKET_MAX_MESSAGE_QUEUE_PER_WORKER: int = 1000
SOCKET_MAX_TCP_KEEPCNT: int = 127
SOCKET_STREAM_LENGTH: int = 1024


# --------------------
# Configurations
# --------------------
ENV_CONF_NAME: str = ".tcp_server.env"
LOG_CONF_NAME: str = "logger.server.conf"
LOG_CONF_NAME_DEFAULT: str = "logger.conf"

DATABASE_NAME: str = "chatbox.sqlite"

# --------------------
# Directories
# --------------------
DIR_ROOT: str = os.path.dirname(os.path.abspath(__file__)).replace('/constants', '').replace('/app', '')
DIR_APP = os.path.join(DIR_ROOT, "app")
DIR_STORAGE = os.path.join(DIR_APP, "storage")
DIR_LOGS = os.path.join(DIR_STORAGE, "logs")
DIR_CRASHES = os.path.join(DIR_LOGS, "crashes")

DIR_DATABASE_SQLITE = os.path.join(DIR_STORAGE, "SQLite")
DIR_DATABASE_MAIN =  os.path.join(DIR_DATABASE_SQLITE, DATABASE_NAME)
DIR_DATABASE_SCHEMA_MAIN =  os.path.join(DIR_APP, "database", "schema", "chatbox.sql")

DIR_CONFIG: str = os.path.join(DIR_ROOT, "../config")
CONFIG_DIRECTORY_RELATIVE_APP: str = "../../../config"



