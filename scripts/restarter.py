import sys
import os
import fcntl
import threading
import time
import subprocess
import multiprocessing
import functools
import logging

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class Tools:
    lock = threading.Lock()
    USE_LOGGER: bool = False

    class PrintColored:
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
        MARGIN_2 = '\033[52m'  # seems equal to MARGIN_1
        # colors
        BLACK = '\033[30m'
        RED_DARK = '\033[31m'
        GREEN_DARK = '\033[32m'
        YELLOW_DARK = '\033[33m'
        BLUE_DARK = '\033[34m'
        PURPLE_DARK = '\033[35m'
        CYAN_DARK = '\033[36m'
        GREY_DARK = '\033[37m'

        BLACK_LIGHT = '\033[90m'
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'

        def __init__(self, root=None):
            self.print_original = print  # old value to the original print function
            self.current_color = self.DEFAULT
            self.root = root

        def __call__(self,
                     *values: object, sep: str | None = None,
                     end: str | None = None,
                     file: str | None = None,
                     flush: bool = True,  # set default to True when using threading
                     color: str | None = None,
                     default_color: str | None = None
                     ):
            if default_color:
                self.current_color = default_color

            default = self.current_color
            if color:
                values = (color, *values, default)  # wrap the content within a selected color as default
            else:
                values = (*values, default)  # wrap the content within a selected color as default
            if self.root:
                values = (self.root, *values)

            with Tools.lock:
                self.print_original(*values, end=end, file=file, flush=flush)

    # alias for shortcuts
    color = PrintColored

    @staticmethod
    def create_logger() -> logging.Logger:
        formatter = logging.Formatter("[%(levelname)-0s] %(asctime)s [%(threadName)-0s]  => %(message)s") # noqa
        _logger_root = logging.getLogger()
        _logger_root.setLevel(logging.INFO)

        handler_file = logging.FileHandler("restarter.log")
        handler_file.setFormatter(formatter)
        _logger_root.addHandler(handler_file)

        handler_stdout = logging.StreamHandler()
        handler_stdout.setFormatter(formatter)
        _logger_root.addHandler(handler_stdout)

        return logging.getLogger("restarter")

    @staticmethod
    def create_colored_printer() -> PrintColored:
        printer = Tools.PrintColored()
        return printer

    class Log:
        def __init__(self):
            self.use_logger = Tools.USE_LOGGER
            self._logger = self.use_logger and Tools.create_logger() or Tools.create_colored_printer()

        def __call__(self,
                     *values: object, sep: str | None = None,
                     end: str | None = None,
                     file: str | None = None,
                     flush: bool = True,  # set default to True when using threading
                     color: str | None = None,
                     default_color: str | None = None,
                     level: int = logging.INFO,
                     **kwargs
                     ):
            if self.use_logger:
                self._logger.log(level, values[0], *values[1:], **kwargs)
            else:
                self._logger(*values, end=end, file=file, flush=flush, color=color, default_color=default_color,
                             **kwargs)

        def debug(self, *args, **kwargs):
            self.__call__(*args, level=logging.DEBUG, **kwargs)

        def info(self, *args, **kwargs):
            self.__call__(*args, level=logging.INFO, **kwargs)

        def warn(self, *args, **kwargs):
            self.__call__(*args, level=logging.WARN, **kwargs)

        def warning(self, *args, **kwargs):
            self.__call__(*args, level=logging.WARNING, **kwargs)

        def error(self, *args, **kwargs):
            self.__call__(*args, level=logging.ERROR, **kwargs)

        def critical(self, *args, **kwargs):
            self.__call__(*args, level=logging.CRITICAL, **kwargs)

        def exception(self, *args, **kwargs):
            self.__call__(*args, level=logging.CRITICAL, **kwargs)


_log = Tools.Log()

_IGNORE_COMMON_DIRS: set[str] = {
    "__pycache__",
    ".idea",
    "venv",
    "env",
    ".git",
    ".hg",
    ".tox",
    ".nox",
    ".pytest_cache",
    ".mypy_cache",
}

class Restarter:
    class EventHandler(PatternMatchingEventHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.restart: threading.Event = threading.Event()
            self.last_reload : float = time.time()
            self.reload_delay: float = 1.00

        def on_modified(self, event):
            if not self._should_reload():
                return

            _log(f" - watcher Detected change of type {event.event_type} in {event.src_path!r}, reloading", color=Tools.color.GREEN_DARK)
            self.last_reload = time.time()
            self.restart.set()

        def _should_reload(self) -> bool:
            now = time.time()
            elapsed = now - self.last_reload
            return elapsed >= self.reload_delay

    def __init__(self, command: tuple[str, ...], path: str, delay_reload: int = .3, delay_stdout: float = 0.25):
        self.name: str = self.__class__.__name__
        _log(f"{self.name} - starting with command {command} , path {path}", color=Tools.color.YELLOW)
        self.process: None|subprocess.Popen[str] = None
        self.io_task_process: None|multiprocessing.Process = None
        self.command: tuple[str, ...] = command
        self.path: str = path
        self.delay_reload: float = delay_reload
        self.delay_stdout: float = delay_stdout
        self.started: threading.Event = threading.Event()
        self.l_padding: str = f'{"------------ <":>20}'
        self.r_padding: str = f'{"> ------------":<20}'

        self.event_handler: Restarter.EventHandler = Restarter.EventHandler(
            patterns=["*.py", "*.pyc"],
            ignore_patterns=[*[f"*/{d}/*" for d in _IGNORE_COMMON_DIRS]],
            case_sensitive=False
        )
        self.observer: Observer = Observer()
        self.observer.schedule(self.event_handler, path, recursive=True)
        self.observer.start()

    def __call__(self):
        process_spawn = functools.partial(
            subprocess.Popen,
            args=self.command,
            preexec_fn=os.setsid,
            bufsize=0,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        try:
            while True:
                try:
                    with process_spawn() as process:
                        self.start(process)
                        self.event_handler.restart.wait()
                        self.stop()
                except KeyboardInterrupt:
                    _log("App stopped manually", color=Tools.color.YELLOW)
                    break

        except KeyboardInterrupt as _:
            pass
        except BaseException as error:
            _log("App stopped with errors, reasons %s" % error, color=Tools.color.RED)
        finally:
            self.shutdown()

    def start(self, process: subprocess.Popen[str]):
        _log(f"{self.l_padding} {self.name} - START {self.r_padding}", color=Tools.color.BLUE)
        time.sleep(self.delay_reload)
        self.started.set()
        self.process = process
        fcntl.fcntl(self.process.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

        self.io_task_process = multiprocessing.Process(target=self.echo_process_stdout, args=())
        self.io_task_process.start()

    def stop(self):
        _log(f"{self.l_padding} {self.name} - STOP {self.r_padding}", color=Tools.color.YELLOW)
        self.event_handler.restart.clear()
        self.started.clear()

        self.process and self.process.terminate()
        self.io_task_process and self.io_task_process.terminate()

        self.process = None
        self.io_task_process = None

    def shutdown(self):
        _log(f"{self.l_padding} {self.name} - SHUTDOWN {self.r_padding}", color=Tools.color.PURPLE_DARK)
        self.stop()
        try:
            self.observer.stop()
            self.observer.join()
        except Exception as error:
            _log("Error while stopping Restarter observer, reason %s %s" % (repr(error), error), color=Tools.color.RED)
        self.echo_process_stdout(run_once=True)  # output possible buffer from stdout after shutdown

    def echo_process_stdout(self, run_once: bool = False) -> None:
        try:
            while True:
                time.sleep(self.delay_stdout)
                sys.stdout.write(self.read_process_stdout())
                sys.stdout.flush()
                if self.event_handler.restart.is_set():
                    break
                if run_once:
                    break
        except KeyboardInterrupt as _:
            return

    def read_process_stdout(self) -> str:

        output: str = ''
        if not self.process:
            return output
        try:
            while True:
                try:
                    buffer_output: bytes = self.process.stdout.read()  # noqa
                    if not buffer_output:
                        break
                    output += buffer_output.decode("UTF-8")
                except IOError as _:
                    break
        except (IOError, ValueError) as _:
            ...
        except Exception as error:
            _log(f"Error while reading stdout buffer from process {self.process.pid}, reason %s %s" % (
            repr(error), error), color=Tools.color.RED)
        return output


def usage():
    print("Usage: restarter <watch_path> <binary> [<binary_args>, ...]")
    exit(1)

def main():
    if len(sys.argv) < 2:
        path = "dummy_app"
        command = ("env/bin/python", "dummy_app/main.py")
    else:
        path = sys.argv[1]
        command = tuple(sys.argv[2:])

    Restarter(command, path)()


TEXT_APP: str = """        

    ____            __             __           
   / __ \___  _____/ /_____ ______/ /____  _____
  / /_/ / _ \/ ___/ __/ __ `/ ___/ __/ _ \/ ___/
 / _, _/  __(__  ) /_/ /_/ / /  / /_/  __/ /    
/_/ |_|\___/____/\__/\__,_/_/   \__/\___/_/     
                                                

"""

if __name__ == "__main__":
    _log(TEXT_APP, color=Tools.color.RED_DARK)
    main()
else:
    _log("Application must run as main and not as package", color=Tools.color.RED)
