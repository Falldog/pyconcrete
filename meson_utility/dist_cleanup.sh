#!/usr/bin/env bash

DIST_DIR='meson-dist/pyconcrete-*'

echo "clean up the dist files in '${DIST_DIR}'"

# this script will be executed when do `python -m build --sdist`
# and this will cleanup the meson staging folder

set -ex

rm -rf ${DIST_DIR}/appveyor/
rm -rf ${DIST_DIR}/bin/
rm -rf ${DIST_DIR}/docker/
rm -rf ${DIST_DIR}/example/
rm -rf ${DIST_DIR}/tests/
