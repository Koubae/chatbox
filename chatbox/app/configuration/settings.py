import os
import dotenv
from types import MappingProxyType

from .. import constants


def configure(env_file_name: str = '.env') -> MappingProxyType:
    configuration_path = os.path.join(constants.DIR_CONFIG, env_file_name)
    dotenv.load_dotenv(configuration_path)

    settings = dict(
        APP_NAME=os.environ.get("APP_NAME") or constants.APP_NAME,
        BACKEND_LOG_CONF_NAME=os.environ.get("BACKEND_LOG_CONF_NAME") or constants.LOG_CONF_NAME_DEFAULT,
    )

    return MappingProxyType(settings)
