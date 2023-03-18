#.ONESHELL:

# Constants
PACKAGE = chatbox
HOST = localIpAddr
PORT = 20020
SERVER = tcp_server
CLIENT = tcp_client
ENVIRONMENT = venv
ENVIRONMENT_SOURCE = venv/bin/activate
PYTHON_DIS = venv/bin/python

up.server:
	$(PYTHON_DIS) -m $(PACKAGE) $(SERVER) $(HOST) $(PORT)

up.client:
	$(PYTHON_DIS) -m $(PACKAGE) $(CLIENT) $(HOST) $(PORT)


# Project set up
init:
	pip install -r requirements.txt


# pytest Flags:
# -rP  Extra summary info
# -s   -s is equivalent to --capture=no.
# -rx  shows the captured output of passed tests.
.test:
	pytest -rP


.PHONY: init test

checkMakefile: # ref https://stackoverflow.com/a/16945143/13903942
	cat -e -t -v Makefile .