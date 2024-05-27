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
from __future__ import unicode_literals

import importlib
import logging
import unittest
from test import base
from test.utility.gen_code_tools import lib_gen_pye
from test.utility.pyconcrete_builder import import_pyconcrete_in_test

logger = logging.getLogger('pyconcrete')


class TestBasic(base.TestPyConcreteBase):
    def test_import(self):
        pyconcrete = import_pyconcrete_in_test()

        logger.info('pyconcrete info="%s", path=%s' % (pyconcrete.info(), pyconcrete.__file__))

        # print(f'pyconcrete={pyconcrete}')
        # print(f'pyconcrete.__name__={pyconcrete.__name__}')
        # print(f'pyconcrete.__file__={pyconcrete.__file__}')
        # print(f'pyconcrete.__loader__={pyconcrete.__loader__}')
        self.assertTrue(pyconcrete.__file__.startswith(self.lib_dir))  # check import correct module

    def test_import_pye(self):
        module_name = 'test_module'
        py_code = b"v_int=1\r\n"
        py_code += b"v_string='abc'\r\n"
        pye_filepath = lib_gen_pye(py_code, f'{module_name}.pye', self.tmp_dir)

        # import testing .pye file for testing
        m = importlib.import_module(module_name)

        self.assertEqual(pye_filepath, m.__file__)  # check import correct module
        self.assertEqual(1, m.v_int)
        self.assertEqual('abc', m.v_string)


if __name__ == '__main__':
    unittest.main()
