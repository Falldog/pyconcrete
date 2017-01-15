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

import base
import unittest


class TestBasic(base.TestPyConcreteBase):
    def test_import(self):
        import pyconcrete

        print('pyconcrete info="%s", path=%s' % (pyconcrete.info(), pyconcrete.__file__))

        # print "lib dir=[%s], pyconcrete __init__=[%s]" % (self.lib_dir, pyconcrete.__file__)
        self.assertTrue(pyconcrete.__file__.startswith(self.lib_dir))  # check import correct module

    def test_import_pye(self):
        py_code = b"v_int=1\r\n"
        py_code += b"v_string='abc'\r\n"
        pye_filepath = self.lib_gen_pye(py_code, 'test_module.pye')

        # import test.pye testing
        import test_module

        self.assertEqual(pye_filepath, test_module.__file__)  # check import correct module
        self.assertEqual(1, test_module.v_int)
        self.assertEqual('abc', test_module.v_string)


if __name__ == '__main__':
    unittest.main()

