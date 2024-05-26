#!/usr/bin/env python
#
# Copyright 2015 Falldog Hsieh <falldog7@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atexit
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from os.path import abspath, dirname, exists, join

from src.config import SECRET_HEADER_PATH

try:
    from importlib import reload
except ImportError:
    pass


PY2 = sys.version_info[0] < 3
ROOT_DIR = abspath(join(dirname(__file__), '..'))
tmp_pyconcrete_dir = None
tmp_pyconcrete_exe = None


def touch(file_path):
    open(file_path, 'a').close()


def build_tmp_pyconcrete(passphrase):
    global tmp_pyconcrete_dir, tmp_pyconcrete_exe
    if tmp_pyconcrete_dir:
        return tmp_pyconcrete_dir

    # remove secret key header, for testing on generate secret-key file
    if os.path.exists(SECRET_HEADER_PATH):
        os.remove(SECRET_HEADER_PATH)

    tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_lib_')

    _ori_dir = os.getcwd()
    os.chdir(ROOT_DIR)
    try:
        # just build
        # force_option = '--force' if force else ''
        # subprocess.check_call('python setup.py build --passphrase=%s %s' % (passphrase, force_option), shell=True)

        cmd = (
            sys.executable,
            'setup.py',
            'install',
            '--passphrase=%s' % passphrase,
            '--install-base=%s' % tmp_dir,
            '--install-purelib=%s' % tmp_dir,
            '--install-platlib=%s' % tmp_dir,
            '--install-scripts=%s' % join(tmp_dir, 'scripts'),
            '--install-headers=%s' % join(tmp_dir, 'headers'),
            '--install-data=%s' % join(tmp_dir, 'data'),
            '--quiet',
        )
        subprocess.check_call(' '.join(cmd), shell=True)

        copy_pyconcrete_ext(tmp_dir)

        exe_name = 'pyconcrete.exe' if sys.platform == 'win32' else 'pyconcrete'
        tmp_pyconcrete_exe = join(tmp_dir, 'scripts', exe_name)
        tmp_pyconcrete_dir = tmp_dir
        print('build tmp pyconcrete at "%s"' % tmp_dir)

        if not exists(tmp_pyconcrete_exe):
            raise ValueError("can't find pyconcrete exe!")
    finally:
        os.chdir(_ori_dir)

    return tmp_pyconcrete_dir


def copy_pyconcrete_ext(tmp_dir):
    tmp_pyconcrete = join(tmp_dir, 'pyconcrete')
    for f in os.listdir(tmp_pyconcrete):
        if re.match(r'^_pyconcrete.*\.(so|dll|pyd)$', f):
            shutil.copy(join(tmp_pyconcrete, f), join(ROOT_DIR, 'src', 'pyconcrete'))
            break


def remove_tmp_pyconcrete():
    global tmp_pyconcrete_dir
    if tmp_pyconcrete_dir:
        shutil.rmtree(tmp_pyconcrete_dir)
        print('remove tmp pyconcrete at "%s"' % tmp_pyconcrete_dir)
        tmp_pyconcrete_dir = None


atexit.register(remove_tmp_pyconcrete)


def get_pyconcrete_env_path():
    """
    append tmp_pyconcrete_dir path into PYTHONPATH
    for subprocess execute script and import the pyconcrete we just builded
    """
    global tmp_pyconcrete_dir
    env = os.environ.copy()
    env.setdefault('PYTHONPATH', '')
    env['PYTHONPATH'] += os.pathsep + tmp_pyconcrete_dir
    return env


# ==================================== TestPyConcreteBase ==================================== #


class TestPyConcreteBase(unittest.TestCase):
    passphrase = 'Falldog'
    force_build = True

    def __init__(self, *argv, **argd):
        unittest.TestCase.__init__(self, *argv, **argd)

    @classmethod
    def setUpClass(cls):
        build_tmp_pyconcrete(cls.passphrase)

        cls.lib_dir = join(ROOT_DIR, 'src')
        cls._cls_sys_path = sys.path[:]
        sys.path.insert(0, cls.lib_dir)

        import pyconcrete

        # force to reload it, avoid to load installed module
        if not pyconcrete.__file__.startswith(cls.lib_dir):
            reload(pyconcrete)

    @classmethod
    def tearDownClass(cls):
        if cls._cls_sys_path:
            sys.path = cls._cls_sys_path
            cls._cls_sys_path = None

    def setUp(self):
        global tmp_pyconcrete_exe
        self.tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_tmp_')
        self._sys_path = sys.path[:]
        sys.path.insert(0, self.tmp_dir)
        self._pyconcrete_exe = tmp_pyconcrete_exe

    def tearDown(self):
        if self._sys_path:
            sys.path = self._sys_path
            self._sys_path = None
        shutil.rmtree(self.tmp_dir)
