#.ONESHELL:

# Constants
APP_DIR = chatbox
HOST = localIpAddr
PORT = 20020
SERVER = tcp_server
CLIENT = tcp_client
ENVIRONMENT = venv
ENVIRONMENT_SOURCE = venv/bin/activate
PYTHON_DIS = venv/bin/python

CLIENT_PASS=1234

up.server:
	$(PYTHON_DIS) -m $(APP_DIR) $(SERVER) $(HOST) $(PORT)

# instance: make up.client user=--user=fede2 password=--password=123
up.client:
	$(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT)

up.client.1:
	$(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT) --user=user001 --password=$(CLIENT_PASS)
up.client.2:
	$(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT) --user=user002 --password=$(CLIENT_PASS)
up.client.3:
	$(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT) --user=user003 --password=$(CLIENT_PASS)
up.client.4:
	$(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT) --user=user004 --password=$(CLIENT_PASS)

up.server.reloader:
	. $(BIN)/activate; python scripts/restarter.py $(APP_DIR) $(PYTHON_DIS) -m $(APP_DIR) $(SERVER) $(HOST) $(PORT)

up.client.reloader:
	. $(BIN)/activate; python scripts/restarter.py $(APP_DIR) $(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT)

up.client.1.reloader:
	. $(BIN)/activate; python scripts/restarter.py $(APP_DIR) $(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT) --user=user001 --password=$(CLIENT_PASS)
up.client.2.reloader:
	. $(BIN)/activate; python scripts/restarter.py $(APP_DIR) $(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT) --user=user002 --password=$(CLIENT_PASS)
up.client.3.reloader:
	. $(BIN)/activate; python scripts/restarter.py $(APP_DIR) $(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT) --user=user003 --password=$(CLIENT_PASS)
up.client.4.reloader:
	. $(BIN)/activate; python scripts/restarter.py $(APP_DIR) $(PYTHON_DIS) -m $(APP_DIR) $(CLIENT) $(HOST) $(PORT) --user=user004 --password=$(CLIENT_PASS)

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

# ------------------
# Tests
# ------------------

# pytest Flags:
# -rP  Extra summary info
# -s   -s is equivalent to --capture=no.
# -rx  shows the captured output of passed tests.
.test:
	pytest -rP
.test:
	. $(BIN)/activate; pytest -rP -W ignore::DeprecationWarning --disable-warnings
.test_coverage:
	. $(BIN)/activate; pytest -rP -W ignore::DeprecationWarning --disable-warnings --cov=$(APP_DIR)
.test_coverage_html:
	. $(BIN)/activate; pytest -rP -W ignore::DeprecationWarning --disable-warnings --cov=$(APP_DIR) --cov-report=html

# ------------------
# Code Inspections
# ------------------
inspect_code:
	flake8 $(APP_DIR)

inspect_code_benchmark:
	flake8 $(APP_DIR) --benchmark

# ------------------
# Tools
# ------------------

.kill_tcp_port:
	fuser -k $(PORT)/tcp

.PHONY: init .test clean .venv .install

checkMakefile: # ref https://stackoverflow.com/a/16945143/13903942
	cat -e -t -v Makefile .