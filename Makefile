PYTHON    = python3
PIP       = pip3
CONFIG    = config.txt

# Colors
GREEN     = \033[0;32m
RED       = \033[0;31m
RESET     = \033[0m

.PHONY: all install run debug clean lint lint-strict re help

all: install

install:
	@echo "$(GREEN)Creating Virtual Environment...$(RESET)"
	python3 -m venv venv
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install .
	./venv/bin/pip install flake8 mypy
	@echo "$(GREEN)Done. Use 'source venv/bin/activate' to start.$(RESET)"


run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

lint:
	@echo "$(GREEN)Checking with flake8...$(RESET)"
	flake8 .
	@echo "$(GREEN)Checking with mypy (required flags)...$(RESET)"
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	@echo "$(RED)Cleaning cache and temporary files...$(RESET)"
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "$(RED)Cleanup completed.$(RESET)"

re: clean install

help:
	@echo "make install      - Install dependencies"
	@echo "make run          - Run the main program"
	@echo "make debug        - Run in debug mode (pdb)"
	@echo "make lint         - Run flake8 and mypy"
	@echo "make clean        - Remove caches and builds"
