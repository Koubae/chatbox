import socket
import logger
import logging


def main():
    LOGGER_CONFIG = "logger.server.conf"
    logger.ColoredFormatter.init(LOGGER_CONFIG)
    _logger = logging.getLogger(__name__)

    host = socket.gethostbyname(socket.gethostname())
    port = 11000
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse socket in TIME_WAIT state
        server.bind((host, port))
        server.listen(1)

        server_name = f'[{id(server)}, {server.fileno()}]'

        _logger.info(f'{server_name} is listening at {(host, port)} ...')
        try:
            while True:
                try:
                    client, address = server.accept()
                    with client:
                        client_id = id(client)
                        client_name = f'CLIENT::[({client_id}, {client.fileno()})] {address}'
                        _logger.info(f'{server_name} new connection {client_name}')

                        while True:
                            data = client.recv(1024)
                            if not data:
                                break
                            msg = data.decode("UTF-8")
                            _logger.info(f'{client_name} Received {len(data)} data from {client}:\n> {client_id}: {msg}')
                            client.send(data)

                        _logger.info(f"{client_name} stop receiving, socket closed")
                except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as conn_error:
                    _logger.error(f"{server_name} got a connection error, reason: {conn_error}")
                except OSError as os_error:
                    _logger.error(f"{server_name} Operating System Error, reason: {os_error}")
                except Exception as exeception:
                    _logger.error(f"{server_name} Something went wrong, reason: {exeception}")
                else:
                    _logger.info(f"{server_name} last client connection closed with no caught errors")
                finally:
                    _logger.info(f"{server_name} listening to a new connection")

        except KeyboardInterrupt as _:
            _logger.warning(f'{server_name} Shutting down...')
        except BaseException as base_exception:
            _logger.exception(f"{server_name} Something went wrong!\nreason: {base_exception}\nShutting down...", exc_info=base_exception)
        finally:
            try:
                server.shutdown(socket.SHUT_RDWR)
            except OSError as error:
                _logger.exception(f'{server_name} Error while shutting down server TCP socket, reason: {error}', exc_info=error)

if __name__ == '__main__':
    main()
