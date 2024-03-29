import logging
import logging.config
import os
import time
import sys

from .. import constants


class Color:
    DEFAULT: str = '\033[0m'
    # Styles
    BOLD: str = '\033[1m'
    ITALIC: str = '\033[3m'
    UNDERLINE: str = '\033[4m'
    UNDERLINE_THICK: str = '\033[21m'
    HIGHLIGHTED: str = '\033[7m'
    HIGHLIGHTED_BLACK: str = '\033[40m'
    HIGHLIGHTED_RED: str = '\033[41m'
    HIGHLIGHTED_GREEN: str = '\033[42m'
    HIGHLIGHTED_YELLOW: str = '\033[43m'
    HIGHLIGHTED_BLUE: str = '\033[44m'
    HIGHLIGHTED_PURPLE: str = '\033[45m'
    HIGHLIGHTED_CYAN: str = '\033[46m'
    HIGHLIGHTED_GREY: str = '\033[47m'

    HIGHLIGHTED_GREY_LIGHT: str = '\033[100m'
    HIGHLIGHTED_RED_LIGHT: str = '\033[101m'
    HIGHLIGHTED_GREEN_LIGHT: str = '\033[102m'
    HIGHLIGHTED_YELLOW_LIGHT: str = '\033[103m'
    HIGHLIGHTED_BLUE_LIGHT: str = '\033[104m'
    HIGHLIGHTED_PURPLE_LIGHT: str = '\033[105m'
    HIGHLIGHTED_CYAN_LIGHT: str = '\033[106m'
    HIGHLIGHTED_WHITE_LIGHT: str = '\033[107m'

    STRIKE_THROUGH: str = '\033[9m'
    MARGIN_1: str = '\033[51m'
    MARGIN_2: str = '\033[52m'  # seems equal to MARGIN_1
    # colors
    BLACK: str = '\033[30m'
    RED_DARK: str = '\033[31m'
    GREEN_DARK: str = '\033[32m'
    YELLOW_DARK: str = '\033[33m'
    BLUE_DARK: str = '\033[34m'
    PURPLE_DARK: str = '\033[35m'
    CYAN_DARK: str = '\033[36m'
    GRAY = '\033[37m'

    BLACK_LIGHT: str = '\033[90m'
    RED: str = '\033[91m'
    GREEN: str = '\033[92m'
    YELLOW: str = '\033[93m'
    BLUE: str = '\033[94m'
    PURPLE: str = '\033[95m'
    CYAN: str = '\033[96m'
    WHITE: str = '\033[97m'


class ColoredFormatter(logging.Formatter, Color):
    _LOGGER_COLOR: dict[str, str] = {
        'DEBUG': Color.GRAY,
        'INFO': Color.GREEN,
        'WARNING': Color.YELLOW,
        'ERROR': Color.HIGHLIGHTED_RED_LIGHT,
        'CRITICAL': Color.HIGHLIGHTED_RED,
    }
    _LOGGER_COLOR_LIGHT: dict[str, str] = {
        'DEBUG': Color.GRAY,
        'INFO': Color.GREEN,
        'WARN': Color.YELLOW,
        'WARNING': Color.YELLOW,
        'ERROR': Color.RED,
        'CRITICAL': Color.RED_DARK,
    }
    _LOGGER_LEVEL: dict[int, str] = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARN: "WARNING",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record) -> str:
        levelname = record.levelname
        if levelname in self._LOGGER_COLOR:
            record.levelname = f"{self._LOGGER_COLOR[levelname]}{levelname}{self.DEFAULT}"
        return logging.Formatter.format(self, record)

    def formatMessage(self, record):
        res = super().formatMessage(record)
        log_separator: str = "LOG-->"
        if record.levelno in (logging.WARNING, logging.WARN, logging.ERROR, logging.CRITICAL):
            # the formatter must have this 'more formatting.... LOG--> $DEFAULT $CYAN%(message)s$DEFAULT' in order for this to work
            log_split = res.split(log_separator)
            log_metadata = log_split[0]
            # remove DEFAULT and cyan (if default formatter is $DEFAULT $CYAN%(message)s$DEFAULT
            log_message = log_split[1].replace(self.DEFAULT, '').replace(self.CYAN, "")
            log_color_level = self._LOGGER_COLOR_LIGHT[self._LOGGER_LEVEL[record.levelno]]
            # Don't add the default for any other possible errors logs or stack trace
            log_message = f"{self.GREEN}{log_separator}{self.DEFAULT}{log_color_level}{log_message}{self.DEFAULT}"
            res = "".join([log_metadata, log_message])

        return res

    @classmethod
    def _props(cls) -> list:
        return sorted(
            [i for i in dir(cls) if not i.startswith('_') and not i.startswith('func') and not i.startswith('format')],
            key=lambda x: (-len(x), x)
        )  # first by length and then alpha. So that longest comes first

    @classmethod
    def func_formatter_message(cls, formatter: str) -> str:
        for prop in cls._props():
            template_item = f'${prop}'
            template_value = getattr(cls, prop)
            if not isinstance(template_value, str):
                continue

            formatter = formatter.replace(template_item, template_value)

        return formatter

    @staticmethod
    def init(config_filename: str, tcp_app_type: str) -> None:
        """Initialize Global logger"""
        def logging_config_initialize() -> FileNotFoundError | None:
            config_path = os.path.join(constants.DIR_CONFIG, config_filename)
            try:
                logging.config.fileConfig(config_path)
            except FileNotFoundError as _error:
                return _error

        def add_color_formatter_to_stdout_handler():
            _stream_handler = logging.root.handlers[1]

            formatter_from_config = _stream_handler.formatter._fmt   # noqa
            formatter = ColoredFormatter.func_formatter_message(formatter_from_config)
            _stream_handler.setFormatter(ColoredFormatter(formatter))

        try:
            exception: FileNotFoundError = logging_config_initialize()
            if not exception:
                add_color_formatter_to_stdout_handler()
        except KeyError as error:
            exception: KeyError = error
        if not exception:
            return

        # Create A crash pad logger
        ColoredFormatter.init_backup_logger()  # Creating a logger on the fly.
        _logger = logging.getLogger(__name__)
        _logger.exception(
            f"Encountered an error while loading the App {tcp_app_type} with env file {config_filename}, reason: %s, Logging Traceback:\n",
            exception, exc_info=exception)
        _logger.error(f"\n{'-' * 30}\nApp closing with errors!\n{'-' * 30}")
        sys.exit(1)

    @staticmethod
    def init_backup_logger():

        crash_log_path = constants.DIR_CRASHES
        if not os.path.exists(constants.DIR_CRASHES):
            os.makedirs(crash_log_path)
        time_now = time.strftime("%Y%m%d%H%M%S")
        log_name = f"log_{time_now}.log"
        log_path = os.path.join(crash_log_path, log_name)

        formatter = logging.Formatter("%(asctime)s CRASHPAD::[%(levelname)s] proc=(%(processName)s %(process)d) t=(%(threadName)s, %(thread)d) "
                                      " | ( %(name)s in %(filename)s::%(funcName)s@%(lineno)04d ) -->  %(message)s")

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logging.basicConfig(level=logging.DEBUG, handlers=[stdout_handler, file_handler])
