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
import py_compile
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


def to_bytes(s):
    if PY2:
        if isinstance(s, unicode):  # noqa: F821
            return s.encode('utf8')
        return s
    else:
        if isinstance(s, str):
            return s.encode('utf8')
        return s


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

    def lib_gen_py(self, py_code, py_filename, folder=None):
        """folder = None -> use @_tmp_dir"""
        if not folder:
            folder = self.tmp_dir
        self.assertTrue(py_filename.endswith('.py'))
        py_filepath = join(folder, py_filename)
        with open(py_filepath, 'wb') as f:
            f.write(to_bytes(py_code))
        return py_filepath

    def lib_gen_pyc(self, py_code, pyc_filename, folder=None, keep_py=False):
        """folder = None -> use @_tmp_dir"""
        if not folder:
            folder = self.tmp_dir
        self.assertTrue(pyc_filename.endswith('.pyc'))
        filename = os.path.splitext(pyc_filename)[0]
        py_filepath = join(folder, filename + '.py')
        pyc_filepath = join(folder, filename + '.pyc')

        # create .py
        with open(py_filepath, 'wb') as f:
            f.write(to_bytes(py_code))

        # create .pyc
        py_compile.compile(py_filepath, cfile=pyc_filepath)

        # remove files
        if not keep_py:
            os.remove(py_filepath)

        return pyc_filepath

    def lib_gen_pye(self, py_code, pye_filename, folder=None, keep_py=False, keep_pyc=False):
        """folder = None -> use @_tmp_dir"""
        if not folder:
            folder = self.tmp_dir
        self.assertTrue(pye_filename.endswith('.pye'))
        filename = os.path.splitext(pye_filename)[0]
        py_filepath = join(folder, filename + '.py')
        pyc_filepath = join(folder, filename + '.pyc')
        pye_filepath = join(folder, filename + '.pye')

        # create .py
        with open(py_filepath, 'wb') as f:
            f.write(to_bytes(py_code))

        # create .pyc
        py_compile.compile(py_filepath, cfile=pyc_filepath)

        # create .pye & remove .py & .pyc
        import pyconcrete

        pyconcrete.encrypt_file(pyc_filepath, pye_filepath)

        # remove files
        if not keep_py:
            os.remove(py_filepath)
        if not keep_pyc:
            os.remove(pyc_filepath)

        return pye_filepath

    def lib_compile_pyc(self, folder, remove_py=False):
        admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
        arg_remove_py = '--remove-py' if remove_py else ''
        subprocess.check_call(
            '%s %s compile --source=%s --pyc %s' % (sys.executable, admin_path, folder, arg_remove_py),
            env=get_pyconcrete_env_path(),
            shell=True,
        )

    def lib_compile_pye(self, folder, remove_py=False, remove_pyc=False):
        admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
        arg_remove_py = '--remove-py' if remove_py else ''
        arg_remove_pyc = '--remove-pyc' if remove_pyc else ''
        subprocess.check_call(
            '%s %s compile --source=%s --pye %s %s'
            % (sys.executable, admin_path, folder, arg_remove_py, arg_remove_pyc),
            env=get_pyconcrete_env_path(),
            shell=True,
        )
