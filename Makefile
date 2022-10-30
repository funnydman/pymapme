run-tests:
	pytest --cov --cov-fail-under=90 --cov-report=term-missing

run-mypy:
	python3 -m mypy src tests

build-package:
	source venv/bin/activate \
	&& poetry export -f requirements.txt | python -m pip wheel --no-deps --wheel-dir=./wheels -r /dev/stdin \
	&& poetry build
