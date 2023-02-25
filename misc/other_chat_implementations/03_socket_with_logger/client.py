import socket
import logger
import logging


def main():
    LOGGER_CONFIG = "logger.client.conf"
    logger.ColoredFormatter.init(LOGGER_CONFIG)
    _logger = logging.getLogger(__name__)
    
    host = socket.gethostbyname(socket.gethostname())
    port = 11000
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse socket if in socket in TIME_WAIT state
        client.connect((host, port))

        client_name = f'[{id(client)}, {client.fileno()}]'
        _logger.info(f"{client_name} connected to {(host, port)}")

        try:
            while True:
                message = input(">>> ")
                client.send(message.encode("UTF-8"))

                echo = client.recv(1024)
                _logger.info(echo.decode("UTF-8"))

        except KeyboardInterrupt as _:
            _logger.error(f'{client_name} Shutting down...')
        except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as _:
            _logger.error(f"{client_name} Server closed connection")
        except OSError as os_error:
            _logger.error(f"{client_name} Operating System Error, reason: {os_error}")
        except BaseException as base_exception:
            _logger.error(f"{client_name} Something went wrong!\nreason: {base_exception}\nShutting down...")
        finally:
            _logger.warning(f'{client_name} Shutting down...')
            try:
                client.shutdown(socket.SHUT_RD)
            except OSError as error:
                if error.errno != 107: # '[Errno 107] Transport endpoint is not connected'
                    _logger.exception(f'{client_name} Error while shutting down server TCP socket, reason: {error}', exc_info=error)
    

if __name__ == '__main__':
    main()
