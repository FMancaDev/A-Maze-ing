VENV        := venv
PYTHON      := $(VENV)/bin/python3
PIP         := $(VENV)/bin/pip
MAIN        := a_maze_ing.py
CONFIG      := config.txt

# cores
GREEN       := \033[0;32m
BLUE        := \033[0;34m
RED         := \033[0;31m
RESET       := \033[0m

.PHONY: all install run debug clean lint re

all: install

install:
	@echo "$(GREEN)Creating Virtual Environment and installing dependencies...$(RESET)"
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install mlx-2.2-py3-none-any.whl || $(PIP) install mlx-2.2-py3-ubuntu-any.whl || echo "MLX wheel not found, skipping..."
	@$(PIP) install .
	@$(PIP) install flake8 mypy
	@echo "$(GREEN)Install complete. Use 'source venv/bin/activate' to enter venv.$(RESET)"

run:
	@if [ ! -f "$(PYTHON)" ]; then echo "$(RED)Error: Run 'make install' first$(RESET)"; exit 1; fi
	@echo "$(BLUE)Step 1: Generating Maze...$(RESET)"
	@$(PYTHON) $(MAIN) $(CONFIG)
	@echo "$(BLUE)Step 2: Launching Graphical Renderer...$(RESET)"
	@$(PYTHON) main.py $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	@echo "$(RED)Cleaning temporary files and venv...$(RESET)"
	@rm -rf $(VENV) build dist *.egg-info .mypy_cache .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -f maze.txt seed_logs.txt
	@echo "$(RED)Cleanup completed.$(RESET)"

lint:
	@echo "$(GREEN)Running linting...$(RESET)"
	@$(VENV)/bin/flake8 .
	@$(VENV)/bin/mypy . --ignore-missing-imports

re: clean install
