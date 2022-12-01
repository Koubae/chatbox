# Constants
PACKAGE = chatbox
HOST = localIpAddr
PORT = 20020
SERVER = server
CLIENT = client
PYTHON_DIS = python # In mac/linux = python3 in Windows it may be python or just py

up.chatbox:  # test the package stand-alone
	$(PYTHON_DIS) -m $(PACKAGE)

up.server:
	$(PYTHON_DIS) -m $(PACKAGE) $(SERVER) $(HOST) $(PORT)

up.client:
	$(PYTHON_DIS) -m $(PACKAGE) $(CLIENT) $(HOST) $(PORT)
