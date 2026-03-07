VENV        := venv
PYTHON      := $(VENV)/bin/python3
PIP         := $(VENV)/bin/pip
MAIN        := a_maze_ing.py
CONFIG      := config.txt

GREEN       := \033[0;32m
RED         := \033[0;31m
RESET       := \033[0m

.PHONY: all install run debug clean lint lint-strict re

all: install

install:
	@echo "$(GREEN)Creating Virtual Environment and installing dependencies...$(RESET)"
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install mlx-2.2-py3-none-any.whl || $(PIP) install mlx-2.2-py3-ubuntu-any.whl
	@$(PIP) install .
	@$(PIP) install flake8 mypy
	@echo "$(GREEN)Install complete. Use 'source $(VENV)/bin/activate' to run manually.$(RESET)"

run:
	@if [ ! -f "$(PYTHON)" ]; then echo "$(RED)Error: Run 'make install' first$(RESET)"; exit 1; fi
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	@echo "$(RED)Cleaning temporary files and venv...$(RESET)"
	@rm -rf $(VENV) build dist *.egg-info .mypy_cache .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "$(RED)Cleanup completed.$(RESET)"

lint:
	@echo "$(GREEN)Running mandatory linting...$(RESET)"
	@$(VENV)/bin/flake8 .
	@$(VENV)/bin/mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	@echo "$(GREEN)Running strict linting...$(RESET)"
	@$(VENV)/bin/flake8 .
	@$(VENV)/bin/mypy . --strict

re: clean install
