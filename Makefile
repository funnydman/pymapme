UNIT_TEST_FOLDER := "tests/unit/"
SOURCE_DIR := "src/"
UNIT_TESTS_FAIL_UNDER := 95

run-unit-tests:
	python3 -m pytest \
	-v \
	--cov-report term-missing \
	--cov-fail-under="${UNIT_TESTS_FAIL_UNDER}" \
	--cov="${SOURCE_DIR}" \
	"${UNIT_TEST_FOLDER}"


run-static-analysis:
	pylint ${SOURCE_DIR} ${UNIT_TEST_FOLDER}
	mypy --show-error-codes ${SOURCE_DIR} ${UNIT_TEST_FOLDER}


build-package:
	source venv/bin/activate \
	&& poetry export -f requirements.txt | python -m pip wheel --no-deps --wheel-dir=./wheels -r /dev/stdin \
	&& poetry build
