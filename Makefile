PYTHON	?= python3
VENV	:= .venv
PY		:= $(VENV)/bin/python
PIP		:= $(VENV)/bin/pip
MAIN	:= pac-man.py
CONFIG	?= config.json

MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports \
			  --disallow-untyped-defs --check-untyped-defs

all: run

$(VENV)/.installed: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt flake8 mypy
	touch $@

install: $(VENV)/.installed

run: install
	$(PY) $(MAIN) $(CONFIG)

debug: install
	$(PY) -m pdb $(MAIN) $(CONFIG)

test: install
	$(PY) -m unittest discover -s tests -t . -v

lint: install
	$(PY) -m flake8 .
	$(PY) -m mypy . $(MYPY_FLAGS)

lint-strict: install
	$(PY) -m flake8 .
	$(PY) -m mypy . --strict

clean:
	find . -path ./$(VENV) -prune -o -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

fclean: clean
	rm -rf $(VENV)

re: fclean install

.PHONY: all install run debug test lint lint-strict clean fclean re
