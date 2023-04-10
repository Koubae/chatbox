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

# instance: make up.client user=--user=fede2 password=--password=123
up.client:
	$(PYTHON_DIS) -m $(PACKAGE) $(CLIENT) $(HOST) $(PORT) $(user) $(password)


up.server.reloader:
	. $(BIN)/activate; python scripts/restarter.py $(PACKAGE) $(PYTHON_DIS) -m $(PACKAGE) $(SERVER) $(HOST) $(PORT)

up.client.reloader:
	. $(BIN)/activate; python scripts/restarter.py $(PACKAGE) $(PYTHON_DIS) -m $(PACKAGE) $(CLIENT) $(HOST) $(PORT) $(user) $(password)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ < LOCAL HOST > ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# Python environment Management
PY_VERSION=3.11
PY_ENV_NAME=venv
BIN=$(PY_ENV_NAME)/bin

# Project set up
init: .venv .install

.venv:
	python$(PY_VERSION) -m venv $(PY_ENV_NAME)

.install:
	. $(BIN)/activate; pip install -r dev_requirements.txt

clean:
	rm -rf venv
	find -iname "*.pyc" -delete

# pytest Flags:
# -rP  Extra summary info
# -s   -s is equivalent to --capture=no.
# -rx  shows the captured output of passed tests.
.test:
	pytest -rP


.PHONY: init .test clean .venv .install

checkMakefile: # ref https://stackoverflow.com/a/16945143/13903942
	cat -e -t -v Makefile .