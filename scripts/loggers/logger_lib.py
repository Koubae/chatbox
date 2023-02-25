import logger
import logging

from src import my_module

# LOGGER_CONFIG = "logger.conf"
# logging.config.fileConfig(LOGGER_CONFIG)




# todo: IMPROVE THIS!
#The background is set with 40 plus the number of the color, and the foreground with 30
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, GRAY = range(8)
BLACK = COLOR_SEQ % (30 + BLACK)
RED = COLOR_SEQ % (30 + RED)
GREEN = COLOR_SEQ % (30 + GREEN)
YELLOW = COLOR_SEQ % (30 + YELLOW)
BLUE = COLOR_SEQ % (30 + BLUE)
MAGENTA = COLOR_SEQ % (30 + MAGENTA)
CYAN = COLOR_SEQ % (30 + CYAN)
GRAY = COLOR_SEQ % (30 + GRAY)

COLORS = {
    'DEBUG': GRAY,
    'INFO': GREEN,
    'WARNING': YELLOW,
    'ERROR': RED,
    'CRITICAL': MAGENTA,
}

COLORS_MAPPING = {
    'BLACK': BLACK,
    'RED': RED,
    'GREEN': GREEN,
    'YELLOW': YELLOW,
    'BLUE': BLUE,
    'MAGENTA': MAGENTA,
    'CYAN': CYAN,
    'GRAY': GRAY,
    'WHITE': '\033[97m',
    'GREENDARK': '\033[32m',
}

def formatter_message(message, use_color = True):
    if use_color:
        colors = ('BLACK', 'RED', 'GREENDARK', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'GRAY', 'WHITE')
        for c in colors:
            message = message.replace(f'${c}', COLORS_MAPPING[c])
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message



# class ColoredFormatter(logging.Formatter):
#     def __init__(self, msg, use_color = True):
#         logging.Formatter.__init__(self, msg)
#         self.use_color = use_color
#
#     def format(self, record):
#         levelname = record.levelname
#         if self.use_color and levelname in COLORS:
#             record.levelname = COLORS[levelname] + levelname + RESET_SEQ
#         return logging.Formatter.format(self, record)


# _stream_handler = logging.root.handlers[1]
# formatter = formatter_message(_stream_handler.formatter._fmt, True)
# _stream_handler.setFormatter(ColoredFormatter(formatter))



_logger = logging.getLogger(__name__)

_logger.info('info message')
_logger.warning('warning message')
_logger.error('error message')


my_module.run()


