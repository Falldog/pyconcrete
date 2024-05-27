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

import shutil
import sys
import tempfile
import unittest
from test.utility.pyconcrete_builder import import_pyconcrete_in_test, pyconcrete_in_test_builder

try:
    from importlib import reload
except ImportError:
    pass


# ==================================== TestPyConcreteBase ==================================== #


def dump_debug_info():
    sys_path = '\n\t'.join(sys.path)
    print(f"sys.path={sys_path}")


class TestPyConcreteBase(unittest.TestCase):
    force_build = True

    def __init__(self, *argv, **argd):
        unittest.TestCase.__init__(self, *argv, **argd)

    @classmethod
    def setUpClass(cls):
        pyconcrete_base_path = pyconcrete_in_test_builder.init()
        sys.path.insert(0, pyconcrete_base_path)
        cls._pyconcrete_base_path = pyconcrete_base_path

        # Don't import pyconcrete directly
        # Avoid to import pyconcrete from code repository to keep the testing code clear.
        pyconcrete = import_pyconcrete_in_test()

        # force to reload it, avoid to load installed module
        if not pyconcrete.__file__.startswith(pyconcrete_base_path):
            reload(pyconcrete)
            print('RELOAD pyconcrete, may be unexpected')

    @classmethod
    def tearDownClass(cls):
        if cls._pyconcrete_base_path:
            try:
                sys.path.remove(cls._pyconcrete_base_path)
            except ValueError:
                pass
            cls._pyconcrete_base_path = None

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_tmp_')
        sys.path.insert(0, self.tmp_dir)
        self._pyconcrete_exe = pyconcrete_in_test_builder.pyconcrete_exe_path

    def tearDown(self):
        sys.path.remove(self.tmp_dir)
        shutil.rmtree(self.tmp_dir)
