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
import shutil
import unittest
import subprocess
from os.path import dirname, abspath, join

import base

ROOT_DIR = abspath(join(dirname(__file__), '..'))
LIB_DIR = join(ROOT_DIR, 'build')
SAMPLE_PACKAGE_DIR = join(ROOT_DIR, 'test', 'data')


class TestAdminScript(base.TestPyConcreteBase):
    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        self._ori_dir = os.getcwd()
        os.chdir(ROOT_DIR)
        
        self.lib_create_temp_env()
        
    def tearDown(self):
        self.lib_remove_temp_env()
        
        os.chdir(self._ori_dir)
    
    def test_parse_folder(self):
        target_dir = join(self.tmp_dir, 'data')
        print 'src=%s, target=%s' % (SAMPLE_PACKAGE_DIR, target_dir)
        shutil.copytree(SAMPLE_PACKAGE_DIR, target_dir)
        
        env = os.environ.copy()
        env.setdefault('PYTHONPATH', '')
        env['PYTHONPATH'] += os.pathsep + self.lib_get_lib_dir()
        subprocess.check_call('python pyconcrete-admin.py compile_all_pye --dir=%s --verbose' % target_dir, env=env, shell=True)


if __name__ == '__main__':
    unittest.main()
