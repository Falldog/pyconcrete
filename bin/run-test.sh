#!/usr/bin/env bash

set -ex

PY_VER=${PY_VER:="3.6"}
TEST_VERBOSE=${TEST_VERBOSE:=""}


declare -xr REPO_ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )
declare -xr PIP_CACHE=${REPO_ROOT}/.pip-cache

mkdir -p ${PIP_CACHE}
cd "${REPO_ROOT}"

build() {
    ver=$1
    service="pye${ver}"

    docker-compose -f docker-compose-test.yml build ${service}
}

run_test() {
    ver=$1
    docker run \
        --rm \
        -t \
        -e TEST_PYE_PERFORMANCE_COUNT=1 \
        -e TEST_VERBOSE=${TEST_VERBOSE} \
        --mount="type=bind,source=${REPO_ROOT}/,target=/code" \
        --mount="type=bind,source=${PIP_CACHE}/,target=/root/.cache/pip/" \
        falldog/pyconcrete-tester:${ver} \
        \
        /bin/bash -c \
        " \
            pip list && \
            python /code/pyconcrete-admin.py test \
        "
}

attach_for_test() {
    ver=$1
    docker run \
        --rm \
        -it \
        -e TEST_PYE_PERFORMANCE_COUNT=1 \
        --mount="type=bind,source=${REPO_ROOT}/,target=/code" \
        --mount="type=bind,source=${PIP_CACHE}/,target=/root/.cache/pip/" \
        falldog/pyconcrete-tester:${ver} \
        /bin/bash
}



case $1 in
    attach)
      build ${PY_VER}
      attach_for_test "${PY_VER}"
      ;;
    *)
      build ${PY_VER}
      run_test "${PY_VER}"
      ;;
esac
