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

import os
import sys
import shutil
import atexit
import unittest
import tempfile
import subprocess
import py_compile
from os.path import dirname, abspath, join, exists
from src.config import SECRET_HEADER_PATH
try:
    from importlib import reload
except ImportError:
    pass


ROOT_DIR = abspath(join(dirname(__file__), '..'))


# # testing ... not complete
# def long_str(x):
#     return ((chr( x        & 0xff)) +
#             (chr((x >> 8)  & 0xff)) +
#             (chr((x >> 16) & 0xff)) +
#             (chr((x >> 24) & 0xff)))
#
#
# # testing ... not complete
# def compile_pyc(codestring, doraise=True):
#     import __builtin__
#     import marshal
#     #with open(file, 'U') as f:
#     #    try:
#     #        timestamp = long(os.fstat(f.fileno()).st_mtime)
#     #    except AttributeError:
#     #        timestamp = long(os.stat(file).st_mtime)
#     #    codestring = f.read()
#     timestamp = 0
#     file = ''
#     try:
#         codeobject = __builtin__.compile(codestring, file, 'exec')
#     except Exception,err:
#         py_exc = py_compile.PyCompileError(err.__class__, err, file)
#         if doraise:
#             raise py_exc
#         else:
#             sys.stderr.write(py_exc.msg + '\n')
#             return
#     pyc_data = marshal.dumps(py_compile.MAGIC + long_str(timestamp) + str(codeobject))
#     return pyc_data


tmp_pyconcrete_dir = None


def touch(file_path):
    open(file_path, 'a').close()


def build_tmp_pyconcrete(passphrase):
    global tmp_pyconcrete_dir
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

        # only copy _pyconcrete.so into src
        # for debugging on current code & so
        subprocess.check_output(
            'cp {src} {dest}'.format(
                src=join(tmp_dir, 'pyconcrete', '_pyconcrete*.so'),
                dest=join(ROOT_DIR, 'src', 'pyconcrete'),
            ),
            shell=True
        )

        tmp_pyconcrete_dir = tmp_dir
        print('build tmp pyconcrete at "%s"' % tmp_dir)
    finally:
        os.chdir(_ori_dir)

    return tmp_pyconcrete_dir


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
        self.tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_tmp_')
        self._sys_path = sys.path[:]
        sys.path.insert(0, self.tmp_dir)

    def tearDown(self):
        if self._sys_path:
            sys.path = self._sys_path
            self._sys_path = None
        shutil.rmtree(self.tmp_dir)

    def lib_gen_py(self, py_code, py_filename, folder=None):
        """ folder = None -> use @_tmp_dir """
        if not folder:
            folder = self.tmp_dir
        self.assertTrue(py_filename.endswith('.py'))
        py_filepath = join(folder, py_filename)
        with open(py_filepath, 'wb') as f:
            f.write(py_code)
        return py_filepath

    def lib_gen_pyc(self, py_code, pyc_filename, folder=None, keep_py=False):
        """ folder = None -> use @_tmp_dir """
        if not folder:
            folder = self.tmp_dir
        self.assertTrue(pyc_filename.endswith('.pyc'))
        filename = os.path.splitext(pyc_filename)[0]
        py_filepath = join(folder, filename + '.py')
        pyc_filepath = join(folder, filename + '.pyc')
        
        # create .py
        with open(py_filepath, 'wb') as f:
            f.write(py_code)

        # create .pyc
        py_compile.compile(py_filepath, cfile=pyc_filepath)
        
        # remove files
        if not keep_py:
            os.remove(py_filepath)
        
        return pyc_filepath

    def lib_gen_pye(self, py_code, pye_filename, folder=None, keep_py=False, keep_pyc=False):
        """ folder = None -> use @_tmp_dir """
        if not folder:
            folder = self.tmp_dir
        self.assertTrue(pye_filename.endswith('.pye'))
        filename = os.path.splitext(pye_filename)[0]
        py_filepath = join(folder, filename + '.py')
        pyc_filepath = join(folder, filename + '.pyc')
        pye_filepath = join(folder, filename + '.pye')
        
        # create .py
        with open(py_filepath, 'wb') as f:
            f.write(py_code)
        
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
        subprocess.check_call('%s %s compile --source=%s --pyc %s' % (sys.executable, admin_path, folder, arg_remove_py), env=get_pyconcrete_env_path(), shell=True)

    def lib_compile_pye(self, folder, remove_py=False, remove_pyc=False):
        admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
        arg_remove_py = '--remove-py' if remove_py else ''
        arg_remove_pyc = '--remove-pyc' if remove_pyc else ''
        subprocess.check_call('%s %s compile --source=%s --pye %s %s' % (sys.executable, admin_path, folder, arg_remove_py, arg_remove_pyc), env=get_pyconcrete_env_path(), shell=True)


