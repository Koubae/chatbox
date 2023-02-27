import os
import dotenv
from types import MappingProxyType

def configure(env_file_name: str = '.env') -> MappingProxyType:
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_directory = "../../../config"
    configuration_path = os.path.join(current_directory, config_directory, env_file_name)
    dotenv.load_dotenv(configuration_path)

    settings = dict(
        APP_NAME = os.environ.get("APP_NAME") or "ChatBox-Master",

        BACKEND_LOG_CONF_NAME = os.environ.get("BACKEND_LOG_CONF_NAME") or "logger.conf",
    )

    return MappingProxyType(settings)
