import logging
import logging.config
import os


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
    MARGIN_2: str = '\033[52m' # seems equal to MARGIN_1
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
    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record) -> str:
        levelname = record.levelname
        if levelname in self._LOGGER_COLOR:
            record.levelname = f"{self._LOGGER_COLOR[levelname]}{levelname}{self.DEFAULT}"
        return logging.Formatter.format(self, record)

    @classmethod
    def _props(cls) -> list:
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
    def init(config_filename) -> None:
        """Initialize Global logger"""

        def loggin_config_initialize():
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_dir = "../../../config"
            config_path = os.path.join(current_dir, config_dir, config_filename)
            logging.config.fileConfig(config_path) # TODO. add proper try/Cath

        def add_color_formatter_to_stdout_handler():
            _stream_handler = logging.root.handlers[1]

            formatter_from_config = _stream_handler.formatter._fmt
            formatter = ColoredFormatter.func_formatter_message(formatter_from_config)
            _stream_handler.setFormatter(ColoredFormatter(formatter))

        loggin_config_initialize()
        add_color_formatter_to_stdout_handler()