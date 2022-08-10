.PHONY: all clean lint type test test-cov

CMD:=poetry run
PYMODULE:=srobo_pitools
TESTS:=tests
EXTRACODE:=
PYTEST_FLAGS:=-vv

all: type test lint

lint:
	$(CMD) flake8 $(PYMODULE) $(TESTS) $(EXTRACODE)

type:
	$(CMD) mypy $(PYMODULE) $(TESTS) $(EXTRACODE)

test:
	$(CMD) pytest $(PYTEST_FLAGS) --cov=$(PYMODULE) $(TESTS)

test-cov:
	$(CMD) pytest $(PYTEST_FLAGS) --cov=$(PYMODULE) $(TESTS) --cov-report html

isort:
	$(CMD) isort $(PYMODULE) $(TESTS) $(EXTRACODE)

clean:
	git clean -Xdf # Delete all files in .gitignore