#!/usr/bin/env bash

set -ex

PY_VER=${PY_VER:="3.6"}


declare -xr REPO_ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )
declare -xr PIP_CACHE=${REPO_ROOT}/.pip-cache

mkdir -p ${PIP_CACHE}
cd "${REPO_ROOT}"

build() {
    pushd docker

    docker-compose build

    popd
}

run_test() {
    ver=$1
    docker run \
        --rm \
        -t \
        -e TEST_PYE_PERFORMANCE_COUNT=1 \
        --mount="type=bind,source=${REPO_ROOT}/,target=/code" \
        --mount="type=bind,source=${PIP_CACHE}/,target=/root/.cache/pip/" \
        falldog/pyconcrete-tester:${ver} \
        \
        /bin/bash -c \
        " \
            pip install -r /code/test/requirements.txt && \
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


build

if [[ "$1" = "attach" ]]; then
    attach_for_test "${PY_VER}"

elif [[ "$1" = "test" ]]; then
    run_test "${PY_VER}"

else
    run_test 3.6
fi
