include ./lib-makefiles/integrity.mk
include ./lib-makefiles/docker.mk

# when you clone the repository, make sure the submodules are cloned as well. git submodule update --init --recursive should do the trick.

SHELL = /bin/bash

.DEFAULT_GOAL := help

ORGNAME := swisstopo
SERVICE_QR_CODE_HTTP_PORT := XXXX # TODO: define the port

CURRENT_DIR := $(shell pwd)
INSTALL_DIR := $(CURRENT_DIR)/.venv
PYTHON_FILES := $(shell find api_diemo/* -type f -name "*.py" -print)

#FIXME: put this variable in config file
PYTHON_VERSION=3.7.4
CURRENT_PYTHON_VERSION := $(shell python3 -c "import sys;t='{v[0]}.{v[1]}.{v[2]}'.format(v=list(sys.version_info[:]));sys.stdout.write(t)")
PYTHON_VERSION_OK := $(shell python3 -c "import sys; t=sys.version_info[0:3]; print(int('{}.{}.{}'.format(*t) == '$(PYTHON_VERSION)'))")
BRANCH : = $(shell git status | grep "On branch" | sed -n -e 's/On branch //p')

# Commands
SYSTEM_PYTHON_CMD := $(shell which python3)
PYTHON_CMD := $(INSTALL_DIR)/bin/python3
PIP_CMD := $(INSTALL_DIR)/bin/pip
FLASK_CMD := $(INSTALL_DIR)/bin/flask
PYPI_URL ?= https://pypi.org/simple/
FLAKE8_CMD := $(INSTALL_DIR)/bin/flake8
AUTOPEP8_CMD := $(INSTALL_DIR)/bin/autopep8
MAKO_CMD := $(INSTALL_DIR)/bin/mako-render
NOSE_CMD := $(INSTALL_DIR)/bin/nosetests
COVERAGE_CMD := $(INSTALL_DIR)/bin/coverage
all: help

# This bit check define the build/python "target": if the system has an acceptable version of python, there will be no need to install python locally.

ifeq ($(PYTHON_VERSION_OK),1)
PYTHON_BINDIR := $(shell dirname $(PYTHON_CMD))
PYTHONHOME :=$(shell eval "cd $(PYTHON_BINDIR); pwd; cd > /dev/null")
build/python:
		@echo $(CURRENT_PYTHON_VERSION)
		@echo $(shell $(PYTHON_CMD) -c "print('OK')")
		mkdir -p build
		touch build/python;
else
build/python: local/bin/python3.7
	touch build/python;

SYSTEM_PYTHON_CMD := $(CURRENT_DIR)/local/bin/python3.7
endif



.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo " \033[1mBUILD TARGETS\033[0m "
	@echo "- setup                        Create the python virtual environment"
	@echo " \033[1mLINTING TOOLS TARGETS\033[0m "
	@echo "- lint                         Lint the python source code"
	@echo "- autolint                     Autloint the python source code"
	@echo " \033[1mLOCAL SERVER TARGETS\033[0m "
	@echo "- serve                        Run the project using the flask debug server"
	@echo "- gunicornserve                Run the project using the gunicorn WSGI server"
	@echo "- dockerserve                  Run the project using the gunicorn WSGI server inside a container"
	@echo "- shutdown                     Stop the aforementioned container"
	@echo " \033[1mDOCKER TOOLS TARGETS\033[0m "
	@echo "- build                        Build a target with the current commit tag. If the git repository is not 'clean', the tag will be 'unstable'"
	@echo "- push                         Push the container to docker hub with the current commit tag"
	@echo " \033[1mTESTS TARGETS\033[0m "
	@echo "- test                         Run the unit and integration tests"
	@echo " \033[1mCLEANING TARGETS\033[0m "
	@echo "- clean                        Clean genereated files"
	@echo "- clean_venv                   Clean python venv"

# Build targets. Calling setup is all that is needed for the local files to be installed as needed. Bundesnetz may cause problem.

python: build/python
    @echo "Python installed"

.PHONY: setup
setup: python .venv/build.timestamp


local/bin/python3.7:
	mkdir -p $(CURRENT_DIR)/local;
	curl -z $(CURRENT_DIR)/local/Python-$(PYTHON_VERSION).tar.xz https://www.python.org/ftp/python/$(PYTHON_VERSION)/Python-$(PYTHON_VERSION).tar.xz -o $(CURRENT_DIR)/local/Python-$(PYTHON_VERSION).tar.xz;
	cd $(CURRENT_DIR)/local && tar -xf Python-$(PYTHON_VERSION).tar.xz && Python-$(PYTHON_VERSION)/configure --prefix=$(CURRENT_DIR)/local/ && make altinstall

.venv/build.timestamp: build/python
    $(SYSTEM_PYTHON_CMD) -m venv $(INSTALL_DIR) && ${PIP_CMD} install --upgrade pip setuptools
    ${PIP_CMD} install requirements.txt
    touch .venv/build.timestamp

# linting tools. Useful for commit hooks and making sure coding conventions are respected.

.PHONY: lint
lint: .venv/build.timestamp
		${FLAKE8_CMD} $(PYTHON_FILES)

.PHONY: autolint
autolint: .venv/build.timestamp
		${AUTOPEP8_CMD} --in-place --aggressive --aggressive --verbose $(PYTHON_FILES)

# Serve targets. Using these will run the application on your local machine. You can either serve with a wsgi front (like it would be within the container), or without.
.PHONY: serve
serve: .venv/build.timestamp
        FLASK_APP=service_qrcode FLASK_DEBUG=1 ${FLASK_CMD} run --host=0.0.0.0 --port=${SERVICE_QR_CODE_HTTP_PORT}

.PHONY: gunicornserve
gunicornserve: .venv/build.timestamp
		${SYSTEM_PYTHON_CMD} wsgi.py

# Test target. if units tests or integration tests become too big, feel free to create multiple targets to allow for readability.
# TODO: once tests are imlpemented, we need the right files here.
.PHONY: test
test:
	${NOSE_CMD} api_diemo/tests/unit_tests/something.py
	${NOSE_CMD} api_diemo/tests/integration_tests/something.py

# Docker related functions. Build and push are self explanatory (might require a docker login for push). Docker serve
# has the same expected comportment as gunicornserve, but inside a container, while docker docker_shutdown provides an
# easy target to kill the containers.

.PHONY: build
build:
    $(call dockerbuild,./,service-qr-code,$(call commit_tags))

.PHONY: push
push: build
	$(call push,service-qr-code,$(call commit_tags))

.PHONY: dockerserve
dockerserve: build
	$(MAKO_CMD) --var app_tag=$(call commit_tags) --var app_port=XXXX docker-compose.yml.in > docker-compose.yml
	docker-compose up -d;
	sleep 10

.PHONY: shutdown
shutdown:
	docker-compose down

# Cleaning functions. clean_venv will only remove the virtual environment, while clean will also remove the local python installation.

.PHONY: clean
clean: clean_venv
	rm -rf local;

.PHONY: clean_venv
clean_venv:
	rm -rf ${INSTALL_DIR};

# DEPLOY placeholders.

.PHONY: deploy
deploy:
    ifeq ($(BRANCH),"develop")
        deploy-dev
    else ifeq ($(BRANCH),"master")
        deploy-prod
    else ifeq ($(findstring("release",$(BRANCH))), "release")
        deploy-int
    else
        @echo "no deploy on personal branches"
    endif

deploy-dev:
    @echo "When all is said and done, this should deploy the service to dev"

deploy-int:
    @echo "When all is said and done, this should deploy the service to int"

deploy-prod:
    @echo "When all is said and done, this should deploy the service to prod"


