import sys

import pytest
from chatbox.app.core.tcp.network_socket import NetworkSocket

class TestNetworkSocket:

    def test_instanciate(self):
        print("Network socket")
        print(NetworkSocket, file=sys.stdout)
        assert "h" == "h"