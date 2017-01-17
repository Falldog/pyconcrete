#!/usr/bin/env python
# 
# Create on : 2017/01/18
#
# @author : Falldog
#
from os.path import join, abspath, dirname, pardir

DEFAULT_KEY = 'Falldog'

ROOT_DIR = abspath(join(dirname(__file__), pardir))
TEST_DIR = 'test'
SRC_DIR = join('src')
PY_SRC_DIR = join(SRC_DIR, 'pyconcrete')
EXT_SRC_DIR = join(SRC_DIR, 'pyconcrete_ext')
SECRET_HEADER_PATH = join(EXT_SRC_DIR, 'secret_key.h')

