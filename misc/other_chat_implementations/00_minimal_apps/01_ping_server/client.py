import socket
import time

def main():
    host = socket.gethostbyname(socket.gethostname())
    port = 11000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse socket if in socket in TIME_WAIT state
        client.connect((host, port))

        client_id = client.fileno()
        client_name = f'CLIENT::[{client_id}, {(host, port)}]'

        print(f"-- {client_name} connected to {(host, port)}")
        try:
            while True:
                client.send("\x00".encode("UTF-8"))
                received = client.recv(1024)
                received_size = len(received)
                msg = received.decode("UTF-8")
                print(f"{received_size} bytes from {(host, port)}: {msg}")
                time.sleep(1)
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