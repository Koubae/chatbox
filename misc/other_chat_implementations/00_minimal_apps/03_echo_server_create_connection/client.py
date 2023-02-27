import socket


def main():
    host = socket.gethostbyname(socket.gethostname())
    port = 11000

    socket_options = [(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)]
    client = socket.create_connection((host, port))

    with client:
        for opt in socket_options:
            client.setsockopt(*opt)

        client_name = f'CLIENT::[{id(client)}, {client.fileno()}]'
        print(f"-- {client_name} connected to {(host, port)}")

        try:
            while True:
                message = input(">>> ")
                client.send(message.encode("UTF-8"))

                echo = client.recv(1024)
                print(echo.decode("UTF-8"))

        except KeyboardInterrupt as _:
            print(f'-- {client_name} Shutting down...')
        except (ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, ConnectionError) as _:
            print(f"-- {client_name} Server closed connection")
        except OSError as os_error:
            print(f"-- {client_name} Operating System Error, reason: {os_error}")
        except BaseException as base_exception:
            print(f"-- {client_name} Something went wrong!\nreason: {base_exception}\nShutting down...")
        finally:
            print(f'-- {client_name} Shutting down...')
            try:
                client.shutdown(socket.SHUT_RD)
            except OSError as error:
                if error.errno != 107: # '[Errno 107] Transport endpoint is not connected'
                    print(f'-- {client_name} Error while shutting down server TCP socket, reason: {error}')


if __name__ == '__main__':
    main()
