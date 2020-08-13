SHELL = /bin/bash

.DEFAULT_GOAL := help

CURRENT_DIR := $(shell pwd)
INSTALL_DIR := $(CURRENT_DIR)/.venv
PYTHON_LOCAL_DIR := $(CURRENT_DIR)/build/local
PYTHON_FILES := $(shell find ./* -type f -name "*.py" -print)

#FIXME: put this variable in config file
PYTHON_VERSION := 3.7.4
SYSTEM_PYTHON_CMD := $(shell ./getPythonCmd.sh ${PYTHON_VERSION} ${PYTHON_LOCAL_DIR})

# default configuration
HTTP_PORT ?= 5000

# Commands
PYTHON_CMD := $(INSTALL_DIR)/bin/python3
PIP_CMD := $(INSTALL_DIR)/bin/pip3
FLASK_CMD := $(INSTALL_DIR)/bin/flask
YAPF_CMD := $(INSTALL_DIR)/bin/yapf
NOSE_CMD := $(INSTALL_DIR)/bin/nose2
PYLINT_CMD := $(INSTALL_DIR)/bin/pylint
all: help

# This bit check define the build/python "target": if the system has an acceptable version of python, there will be no need to install python locally.

ifneq ($(SYSTEM_PYTHON_CMD),)
build/python:
	@echo "Using system" $(shell $(SYSTEM_PYTHON_CMD) --version 2>&1)
	@echo $(shell $(SYSTEM_PYTHON_CMD) -c "print('OK')")
	mkdir -p build
	touch build/python
else
build/python: $(PYTHON_LOCAL_DIR)/bin/python3.7
	@echo "Using local" $(shell $(SYSTEM_PYTHON_CMD) --version 2>&1)
	@echo $(shell $(SYSTEM_PYTHON_CMD) -c "print('OK')")

SYSTEM_PYTHON_CMD := $(PYTHON_LOCAL_DIR)/bin/python3.7
endif



.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo -e " \033[1mBUILD TARGETS\033[0m "
	@echo "- setup              Create the python virtual environment"
	@echo -e " \033[1mLINTING TOOLS TARGETS\033[0m "
	@echo "- lint               Lint and format the python source code"
	@echo "- test               Run the tests"
	@echo -e " \033[1mLOCAL SERVER TARGETS\033[0m "
	@echo "- serve              Run the project using the flask debug server. Port can be set by Env variable HTTP_PORT (default: 5000)"
	@echo "- gunicornserve      Run the project using the gunicorn WSGI server. Port can be set by Env variable DEBUG_HTTP_PORT (default: 5000)"
	@echo "- dockerbuild        Build the project localy using the gunicorn WSGI server inside a container"
	@echo "- dockerrun          Run the project using the gunicorn WSGI server inside a container (exposed port: 5000)"
	@echo "- shutdown           Stop the aforementioned container"
	@echo -e " \033[1mCLEANING TARGETS\033[0m "
	@echo "- clean              Clean genereated files"
	@echo "- clean_venv         Clean python venv"

# Build targets. Calling setup is all that is needed for the local files to be installed as needed. Bundesnetz may cause problem.

python: build/python
	@echo $(shell $(SYSTEM_PYTHON_CMD) --version 2>&1) "installed"

.PHONY: setup
setup: python .venv/build.timestamp


$(PYTHON_LOCAL_DIR)/bin/python3.7:
	@echo "Building a local python..."
	mkdir -p $(PYTHON_LOCAL_DIR);
	curl -z $(PYTHON_LOCAL_DIR)/Python-$(PYTHON_VERSION).tar.xz https://www.python.org/ftp/python/$(PYTHON_VERSION)/Python-$(PYTHON_VERSION).tar.xz -o $(PYTHON_LOCAL_DIR)/Python-$(PYTHON_VERSION).tar.xz;
	cd $(PYTHON_LOCAL_DIR) && tar -xf Python-$(PYTHON_VERSION).tar.xz && Python-$(PYTHON_VERSION)/configure --prefix=$(PYTHON_LOCAL_DIR)/ && make altinstall

.venv/build.timestamp: build/python
	$(SYSTEM_PYTHON_CMD) -m venv $(INSTALL_DIR) && $(PIP_CMD) install --upgrade pip setuptools
	${PIP_CMD} install -r dev_requirements.txt
	$(PIP_CMD) install -r requirements.txt
	touch .venv/build.timestamp

# linting target, calls upon yapf to make sure your code is easier to read and respects some conventions.

.PHONY: lint
lint: .venv/build.timestamp
	$(YAPF_CMD) -p -i --style .style.yapf $(PYTHON_FILES)
	$(PYLINT_CMD) $(PYTHON_FILES)

.PHONY: test
test: .venv/build.timestamp
	$(NOSE_CMD) -c tests/unittest.cfg -s tests/

# Serve targets. Using these will run the application on your local machine. You can either serve with a wsgi front (like it would be within the container), or without.
.PHONY: serve
serve: .venv/build.timestamp
	FLASK_APP=service_qrcode FLASK_DEBUG=1 $(FLASK_CMD) run --host=0.0.0.0 --port=$(HTTP_PORT)

.PHONY: gunicornserve
gunicornserve: .venv/build.timestamp
	${PYTHON_CMD} wsgi.py

# Docker related functions.

.PHONY: dockerbuild
dockerbuild:
	docker build -t swisstopo/service-qrcode:local .

export-http-port:
	@export HTTP_PORT=$(HTTP_PORT)

.PHONY: dockerrun
dockerrun: export-http-port
	docker-compose up -d;
	sleep 10

.PHONY: shutdown
shutdown: export-http-port
	docker-compose down

# Cleaning functions. clean_venv will only remove the virtual environment, while clean will also remove the local python installation.

.PHONY: clean
clean: clean_venv
	rm -rf build;

.PHONY: clean_venv
clean_venv:
	rm -rf ${INSTALL_DIR};
