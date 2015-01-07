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
SAMPLE_PACKAGE_DIR = join(ROOT_DIR, 'test', 'data')

def get_build_lib_dir():
    for f in os.listdir(LIB_DIR):
        if f.startswith('lib.'):
            return join(LIB_DIR, f)
    return None

class TestAdmin(unittest.TestCase):
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
        p = get_build_lib_dir()
        if not p:
            raise Excpetion("can't find build lib dir!")
        
        sys.path.append(p)
        sys.path.append(SRC_DIR)
        
    def tearDown(self):
        os.chdir(self._ori_dir)
        sys.path = self._sys_path
        shutil.rmtree(self._tmp_dir)
    
    def test_parse_folder(self):
        target_dir = join(self._tmp_dir, 'data')
        print 'src=%s, target=%s' % (SAMPLE_PACKAGE_DIR, target_dir)
        shutil.copytree(SAMPLE_PACKAGE_DIR, target_dir)
        
        env = os.environ.copy()
        if 'PYTHONPATH' not in env:
            env['PYTHONPATH'] = ''
        env['PYTHONPATH'] += os.pathsep + get_build_lib_dir()
        env['PYTHONPATH'] += os.pathsep + SRC_DIR
        subprocess.check_call('python pyconcrete-admin.py build_pye=%s --verbose --recursive' % target_dir, env=env)
    
if __name__ == '__main__':
    unittest.main()
