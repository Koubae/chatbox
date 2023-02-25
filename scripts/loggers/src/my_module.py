import logging
from .package import module_in_package
_logger = logging.getLogger(__name__)

print(_logger)


def run():
    _logger.info("Started")
    module_in_package.some_func()
