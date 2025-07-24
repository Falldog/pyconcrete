#!/usr/bin/env bash

set -e

PORT=${PORT:="5151"}
NAME=${NAME:="admin"}
PW=${PW:="1234"}

declare -xr REPO_ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )

cd ${REPO_ROOT}

docker build \
    -t falldog/example-django \
    -f example/django/Dockerfile \
    --build-arg NAME=${NAME} \
    --build-arg PW=${PW} \
    .

echo "Django testing website running at http://127.0.0.1:${PORT}"
echo "You also able to browse Django admin page http://127.0.0.1:${PORT}/admin"
echo "Name: ${NAME}"
echo "Password: ${PW}"
echo ""

docker run \
    --rm \
    -p ${PORT}:80 \
    --name pyconcrete-example-django \
    falldog/example-django
