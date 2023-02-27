# Constants
PACKAGE = chatbox
HOST = localIpAddr
PORT = 20020
SERVER = server
CLIENT = client
ENVIRONMENT = venv
PYTHON_DIS = venv/bin/python

up.server:
	$(PYTHON_DIS) -m $(PACKAGE) $(SERVER) $(HOST) $(PORT)

up.client:
	$(PYTHON_DIS) -m $(PACKAGE) $(CLIENT) $(HOST) $(PORT)
