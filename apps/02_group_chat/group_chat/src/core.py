import sys
from .client import app as client_app
from .server import app as server_app
from . import constants
from . import utils

def main():

    if len(sys.argv) < 4:
        print(constants.TITLE)
        print(constants.USAGE)
        sys.exit(0)

    _, server_type, host, port = sys.argv
    # Run parameters validations
    if server_type not in constants.SERVER_TYPES:
        print(f"Server of type {server_type} is not a valid one, possible are {constants.SERVER_TYPES}")
        sys.exit(1)

    if host == constants.DEFAULT_IP_ADDR:
        host = utils.get_local_ipaddr()
    try:
        port = int(port)
    except ValueError as error:
        print(f"Error::<{repr(error)}> | Port must be a numeric type between 1 and 65353, {port} is of type {type(port)}")
        sys.exit(1)

    try:
        if server_type == "client":
            client_app.run((host, port))
        else:
            server_app.run((host, port))

    except KeyboardInterrupt as _:
        print(f'[(interrupted by signal 2: SIGINT)] Closing {server_type} ....')
        sys.exit(130)
    except Exception as exception:
        print(f'[{str(exception)}] Exception Occurred Closing {server_type} ....')
        sys.exit(1)
    except BaseException as base_exception:
        print(f'[{str(base_exception)}] Base Exception Occurred Closing {server_type} ....')
        sys.exit(1)
