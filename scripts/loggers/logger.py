import logging
import logging.config




class Color:
    DEFAULT = '\033[0m'
    # Styles
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    UNDERLINE_THICK = '\033[21m'
    HIGHLIGHTED = '\033[7m'
    HIGHLIGHTED_BLACK = '\033[40m'
    HIGHLIGHTED_RED = '\033[41m'
    HIGHLIGHTED_GREEN = '\033[42m'
    HIGHLIGHTED_YELLOW = '\033[43m'
    HIGHLIGHTED_BLUE = '\033[44m'
    HIGHLIGHTED_PURPLE = '\033[45m'
    HIGHLIGHTED_CYAN = '\033[46m'
    HIGHLIGHTED_GREY = '\033[47m'

    HIGHLIGHTED_GREY_LIGHT = '\033[100m'
    HIGHLIGHTED_RED_LIGHT = '\033[101m'
    HIGHLIGHTED_GREEN_LIGHT = '\033[102m'
    HIGHLIGHTED_YELLOW_LIGHT = '\033[103m'
    HIGHLIGHTED_BLUE_LIGHT = '\033[104m'
    HIGHLIGHTED_PURPLE_LIGHT = '\033[105m'
    HIGHLIGHTED_CYAN_LIGHT = '\033[106m'
    HIGHLIGHTED_WHITE_LIGHT = '\033[107m'

    STRIKE_THROUGH = '\033[9m'
    MARGIN_1 = '\033[51m'
    MARGIN_2 = '\033[52m' # seems equal to MARGIN_1
    # colors
    BLACK = '\033[30m'
    RED_DARK = '\033[31m'
    GREEN_DARK = '\033[32m'
    YELLOW_DARK = '\033[33m'
    BLUE_DARK = '\033[34m'
    PURPLE_DARK = '\033[35m'
    CYAN_DARK = '\033[36m'
    GRAY = '\033[37m'

    BLACK_LIGHT = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

class ColoredFormatter(logging.Formatter, Color):
    _LOGGER_COLOR = {
        'DEBUG': Color.GRAY,
        'INFO': Color.GREEN,
        'WARNING': Color.YELLOW,
        'ERROR': Color.HIGHLIGHTED_RED_LIGHT,
        'CRITICAL': Color.HIGHLIGHTED_RED,
    }
    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        levelname = record.levelname
        if levelname in self._LOGGER_COLOR:
            record.levelname = f"{self._LOGGER_COLOR[levelname]}{levelname}{self.DEFAULT}"
        return logging.Formatter.format(self, record)

    @classmethod
    def _props(cls):
        return sorted(
            [i for i in dir(cls) if not i.startswith('_') and not i.startswith('func') and not i.startswith('format')],
            key= lambda x: (-len(x), x)
        ) # first by length and then alpha. So that longest comes first

    @classmethod
    def func_formatter_message(csl, formatter: str) -> str:
        for prop in csl._props():
            template_item = f'${prop}'
            template_value = getattr(csl, prop)
            if not isinstance(template_value, str):
                continue

            formatter = formatter.replace(template_item, template_value)

        return formatter

    @staticmethod
    def init() -> None:
        """Initialize Global logger"""

        def loggin_config_initialize():
            LOGGER_CONFIG = "logger.conf"
            logging.config.fileConfig(LOGGER_CONFIG)

        def add_color_formatter_to_stdout_handler():
            _stream_handler = logging.root.handlers[0]

            formatter_from_config = _stream_handler.formatter._fmt
            formatter = ColoredFormatter.func_formatter_message(formatter_from_config)
            _stream_handler.setFormatter(ColoredFormatter(formatter))

        loggin_config_initialize()
        add_color_formatter_to_stdout_handler()

ColoredFormatter.init()