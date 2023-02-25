import socket


def main():
    host = socket.gethostbyname(socket.gethostname())
    port = 11000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse socket if in socket in TIME_WAIT state
        server.bind((host, port))
        server.listen(1)

        server_id = server.fileno()
        server_name = f'SERVER::[{server_id}, {(host, port)}]'

        print(f'-- {server_name} is listening at {(host, port)} ...')

        try:
            while True:
                try:
                    client, address = server.accept()
                    with client:
                        clientfd = client.fileno()
                        client_name = f'CLIENT::[{id(client)} {clientfd}, {address}]'
                        print(f"-- {client_name} connection in {address}, listening for receiving")
                        while True:
                            data = client.recv(1024)
                            if not data:
                                break
                            print(f'-- {client_name} Received {len(data)} data from {client}')
                            client.send(f"Ping {host}:{port}".encode("UTF-8"))

                    print(f"-- {client_name} stop receiving, socket closed")
                except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as conn_error:
                    print(f"-- {server_name} got a connection error, reason: {conn_error}")
                except OSError as os_error:
                    print(f"-- {server_name} Operating System Error, reason: {os_error}")
                except Exception as exeception:
                    print(f"-- {server_name} Something went wrong, reason: {exeception}")
                else:
                    print(f"-- {server_name} last client connection closed with no caught errors")
                finally:
                    print(f"-- {server_name} listening to a new connection")

        except KeyboardInterrupt as _:
            print(f'-- {server_name} Shutting down...')
        except BaseException as base_exception:
            print(f"-- {server_name} Something went wrong!\nreason: {base_exception}\nShutting down...")
        finally:
            try:
                server.shutdown(socket.SHUT_RDWR)
            except OSError as error:
                print(f'-- {server_name} Error while shutting down server TCP socket, reason: {error}')



if __name__ == '__main__':
    main()

