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
import unittest
import tempfile
import subprocess
import py_compile
from os.path import dirname, abspath, join, exists

ROOT_DIR = abspath(join(dirname(__file__), '..'))
LIB_DIR = join(ROOT_DIR, 'build')


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


class TestPyConcreteBase(unittest.TestCase):
    passphrase = 'Falldog'
    
    def __init__(self, *argv, **argd):
        unittest.TestCase.__init__(self, *argv, **argd)
        self.lib_dir = None
        self.tmp_dir = None
    
    def lib_get_lib_dir(self):
        if self.lib_dir:
            return self.lib_dir
        for f in os.listdir(LIB_DIR):
            if f.startswith('lib.'):
                self.lib_dir = join(LIB_DIR, f)
                return self.lib_dir
        return None
        
    def lib_build(self, passphrase='Falldog', force=False):
        _ori_dir = os.getcwd()
        os.chdir(ROOT_DIR)
        try:
            force_option = '--force' if force else ''
            subprocess.check_call('python setup.py build --passphrase=%s %s' % (passphrase, force_option))
        finally:
            os.chdir(_ori_dir)
            
    def lib_create_temp_env(self, passphrase='Falldog', force=False):
        self._sys_path = sys.path
        
        self.tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_tmp_')
        
        _ori_dir = os.getcwd()
        os.chdir(ROOT_DIR)
        try:
            force_option = '--force' if force else ''
            subprocess.check_call('python setup.py build --passphrase=%s %s' % (passphrase, force_option), shell=True)
            #subprocess.check_call('python setup.py install --passphrase=%s --install-lib="%s" --install-scripts="%s"' % (passphrase, _tmp_dir, _tmp_dir), shell=True)
        finally:
            os.chdir(_ori_dir)
            
        lib_dir = self.lib_get_lib_dir()
        sys.path.insert(0, lib_dir)
        sys.path.insert(0, self.tmp_dir)
        
        return self.tmp_dir
    
    def lib_remove_temp_env(self):
        if self.tmp_dir and exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir = None
        
        if self._sys_path:
            sys.path = self._sys_path
            self._sys_path = None
    
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
        py_compile.compile(py_filepath)
        
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
        py_compile.compile(py_filepath)
        
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
        env = os.environ.copy()
        env.setdefault('PYTHONPATH', '')
        env['PYTHONPATH'] += os.pathsep + self.lib_get_lib_dir()
        
        admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
        arg_remove_py = '--remove-py' if remove_py else ''
        subprocess.check_call('python %s compile --source=%s --pyc %s' % (admin_path, folder, arg_remove_py), env=env, shell=True)
    
    def lib_compile_pye(self, folder, remove_py=False, remove_pyc=False):
        env = os.environ.copy()
        env.setdefault('PYTHONPATH', '')
        env['PYTHONPATH'] += os.pathsep + self.lib_get_lib_dir()
        
        admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
        arg_remove_py = '--remove-py' if remove_py else ''
        arg_remove_pyc = '--remove-pyc' if remove_pyc else ''
        subprocess.check_call('python %s compile --source=%s --pye %s %s' % (admin_path, folder, arg_remove_py, arg_remove_pyc), env=env, shell=True)


