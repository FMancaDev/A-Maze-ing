PYTHON    = python3
PIP       = pip3
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
	@echo "make install - installs the package locally"
	@echo "make run - Runs the generator with the config.txt file"
	@echo "make test - Runs with a random seed"
	@echo "make flake8 - Checks the code style"
	@echo "make clean - Removes temporary files and logs"
	@echo "make re - Reinstalls everything"

install:
	@echo "$(GREEN)Instalando o pacote $(PACKAGE)...$(RESET)"
	$(PIP) install .
	@echo "$(GREEN)Instalação concluída!$(RESET)"

run:
	@echo "$(GREEN)A gerar labirinto com $(CONFIG)...$(RESET)"
	$(PYTHON) a_maze_ing.py $(CONFIG)

test:
	@echo "$(GREEN)A testar com SEED aleatória: $(SEED)$(RESET)"
	$(PACKAGE) $(CONFIG) $(SEED)

flake8:
	@echo "$(GREEN)A verificar conformidade com PEP 8 (Flake8)...$(RESET)"
	flake8 . --max-line-length=88 --exclude=venv,build,dist
	@echo "$(GREEN)Código limpo!$(RESET)"

clean:
	@echo "$(RED)Limpando ficheiros temporários...$(RESET)"
	rm -rf build/ dist/ *.egg-info .pytest_cache
	rm -f seed_logs.txt maze.txt
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "$(RED)Limpeza concluída.$(RESET)"

re: clean install
