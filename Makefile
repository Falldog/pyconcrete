DEFAULT_TEST_PY_VER = 3.10

.PHONY: help test run-example-django

help:
	@printf "Usage: make [OPTION]\n"
	@printf "\n"
	@printf "test [version: 3.7|3.8|3.9|3.10|...]\n"
	@printf "attach [version: 3.7|3.8|3.9|3.10|...]\n"
	@printf "run-example-django\n"

test:
	VER="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ -z "$$VER" ]; then \
	    VER="$(DEFAULT_TEST_PY_VER)"; \
	fi; \
	\
	PY_VER=$$VER ./bin/run-test.sh

attach:
	VER="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ -z "$$VER" ]; then \
	    VER="$(DEFAULT_TEST_PY_VER)"; \
	fi; \
	\
	PY_VER=$$VER ./bin/run-test.sh attach

run-example-django:
	./bin/run-example-django.sh


# prevent error when assign extra argument for target
%:
	@:
