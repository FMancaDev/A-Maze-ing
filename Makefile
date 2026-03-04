PYTHON    = python3
PIP       = pip3
PACKAGE   = a-maze-ing
CONFIG    = config.txt
SEED      = $(shell echo $$RANDOM)

# cores
GREEN    = \033[0;32m
RED      = \033[0;31m
RESET    = \033[0m

.PHONY: all install run test clean flake8 re help

all: install

help:
	@echo "Available Commands"
	@echo "make install - install package localy"
