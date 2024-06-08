PYTHON_PROJECT_PATH := `pyenv which python`

##@ Subcommands
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[\/0-9a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation
deps/pre: ## Install base setup tools
	pyenv install -s 3.11
	pyenv local 3.11
	$(PYTHON_PROJECT_PATH) -m pip install -U pip wheel
	poetry env use $(PYTHON_PROJECT_PATH)

deps/install:: deps/pre ## Install the dependencies needed for a production installation
	poetry install

deps/install-dev:: deps/pre deps/install ## Install the dependencies needed for a development installation
	poetry install --with dev

##@ Development tools
tests::  ## Run tests
	python3 -m pytest -v tests

lint:   ## Run linters
	pylint pymapme/ tests/
	mypy --show-error-codes pymapme/ tests/

build-package:
	source venv/bin/activate \
	&& poetry export -f requirements.txt | python -m pip wheel --no-deps --wheel-dir=./wheels -r /dev/stdin \
	&& poetry build
