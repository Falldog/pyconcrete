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
from os.path import dirname, abspath, join

ROOT_DIR = abspath(join(dirname(__file__), '..'))
LIB_DIR = join(ROOT_DIR, 'build')
SRC_DIR = join(ROOT_DIR, 'src')

def get_build_lib_dir():
    for f in os.listdir(LIB_DIR):
        if f.startswith('lib.'):
            return join(LIB_DIR, f)
    return None

class TestBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self._ori_dir = os.getcwd()
        self._sys_path = sys.path
        self._tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_tmp_')
        
        os.chdir(ROOT_DIR)
        subprocess.check_call('python setup.py build --passphrase=Falldog')
        p = get_build_lib_dir()
        if not p:
            raise Excpetion("can't find build lib dir!")
        
        sys.path.append(p)
        sys.path.append(SRC_DIR)
        
    def tearDown(self):
        os.chdir(self._ori_dir)
        sys.path = self._sys_path
        shutil.rmtree(self._tmp_dir)
    
    def test_import(self):
        import pyconcrete
        print pyconcrete.info()
    
    def __test_encrypt_decrypt_file(self, py_code):
        py_filename = join(self._tmp_dir, 'test.py')
        pye_filename = join(self._tmp_dir, 'test.pye')
        with open(py_filename, 'wb') as f:
            f.write(py_code)
            
        import pyconcrete
        print 'py code len=%d' % len(py_code)
        print 'encrypt_file : %s' % py_filename
        pyconcrete.encrypt_file(py_filename, pye_filename)
        with open(pye_filename, 'rb') as f:
            data = f.read()
        print 'decrypt_buffer'
        result = pyconcrete.decrypt_buffer(data)
        self.assertEqual(py_code, result)
    
    def test_process_py_code_empty(self):
        py_code = ''
        self.__test_encrypt_decrypt_file(py_code)
        
    def test_process_py_code_large(self):
        py_code = ''
        for i in xrange(100):
            py_code += 'print "This is testing large py file ... %d"\r\n' % i
        self.__test_encrypt_decrypt_file(py_code)
    
    def test_process_py_code_1_block(self):
        py_code = 'v=12345678901234'
        self.assertEqual(16, len(py_code))
        self.__test_encrypt_decrypt_file(py_code)
    
    def test_process_py_code_less_1_block(self):
        py_code = 'v=123456789'
        self.assertLess(len(py_code), 16)
        self.__test_encrypt_decrypt_file(py_code)
    
    def test_process_py_code_2_block(self):
        py_code  = 'v1=123456789\r\n'
        py_code += 'v2=123456789\r\n'
        self.assertLess(len(py_code), 32)
        self.__test_encrypt_decrypt_file(py_code)
    
    def test_import_pye(self):
        py_code = "v_int=1\r\n"
        py_code += "v_string='abc'\r\n"
        py_filename = join(self._tmp_dir, 'test.py')
        pyc_filename = join(self._tmp_dir, 'test.pyc')
        pye_filename = join(self._tmp_dir, 'test.pye')
        with open(py_filename, 'wb') as f:
            f.write(py_code)
        
        py_compile.compile(py_filename)
        
        import pyconcrete
        pyconcrete.encrypt_file(pyc_filename, pye_filename)
        os.remove(py_filename)
        os.remove(pyc_filename)
        
        sys.path.insert(0, self._tmp_dir)
        import test
        self.assertEqual(1, test.v_int)
        self.assertEqual('abc', test.v_string)
    
if __name__ == '__main__':
    unittest.main()
