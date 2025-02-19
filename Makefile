DEFAULT_TEST_PY_VER = 3.10
PY_VERSIONS = 3.7 3.8 3.9 3.10 3.11 3.12 3.13

.PHONY: help test attach

help:
	@printf "Usage: make [OPTION]\n"
	@printf "\n"
	@printf "test-all\n"
	@printf "test [version: 3.7|3.8|3.9|3.10|...]\n"
	@printf "attach [version: 3.7|3.8|3.9|3.10|...]\n"
	@printf "run-example-django\n"
	@printf "build-dist\n"
	@printf "upload-dist\n"
	@printf "upload-dist-for-test\n"
	@printf "testpypi-install {ENV: VERSION= PASSPHRASE=}\n"

test:
	VER="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ -z "$$VER" ]; then \
	    VER="$(DEFAULT_TEST_PY_VER)"; \
	fi; \
	\
	PY_VER=$$VER ./bin/run-test.sh

test-all :
	for ver in $(PY_VERSIONS); do \
	    PY_VER=$$ver ./bin/run-test.sh; \
	done

attach:
	VER="$(filter-out $@,$(MAKECMDGOALS))"; \
	if [ -z "$$VER" ]; then \
	    VER="$(DEFAULT_TEST_PY_VER)"; \
	fi; \
	\
	PY_VER=$$VER ./bin/run-test.sh attach

run-example-django:
	./bin/run-example-django.sh

build-dist:
	rm -rf dist/
	if [ -z "$$(git status --porcelain --untracked-files=no)" ]; then \
        python -m build --sdist -Csetup-args="-Dpassphrase=__DUMMY__" ; \
	else \
		echo "Please stash your local modification before build dist ..."; \
	fi;

upload-dist:
	twine upload dist/*

upload-dist-for-test:
	twine upload -r testpypi dist/*

testpypi-install:
	python3 -m pip install \
		--index-url https://test.pypi.org/simple/ \
		--extra-index-url https://pypi.org/simple/ \
		--no-cache-dir \
		pyconcrete==$(VERSION) \
		-Csetup-args="-Dpassphrase=$(PASSPHRASE)"

# prevent error when assign extra argument for target
%:
	@:
