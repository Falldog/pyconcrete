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


class TestConcrete(base.TestPyConcreteBase):
    def test_decrypt_exception(self):
        import pyconcrete
        print(pyconcrete.__file__)
        data = 'abc'
        self.assertLess(len(data), 16)
        
        with self.assertRaises(pyconcrete._pyconcrete.Error):
            pyconcrete.decrypt_buffer(data)

    def __do_encrypt_decrypt_file(self, py_code):
        py_filepath = self.lib_gen_py(py_code, 'test.py')
        pye_filepath = py_filepath + 'e'
        
        import pyconcrete
        pyconcrete.encrypt_file(py_filepath, pye_filepath)
        
        with open(pye_filepath, 'rb') as f:
            data = f.read()
        return pyconcrete.decrypt_buffer(data)

    def test_process_py_code_empty(self):
        py_code = b''
        res = self.__do_encrypt_decrypt_file(py_code)
        self.assertEqual(py_code, res)

    def test_process_py_code_large(self):
        py_code = ''
        for i in range(100):
            py_code += ('print("This is testing large py file ... %s")\r\n' % i)
        res = self.__do_encrypt_decrypt_file(py_code.encode('utf8'))
        self.assertEqual(py_code, res.decode('utf8'))

    def test_process_py_code_1_block(self):
        py_code = b'v=12345678901234'
        self.assertEqual(16, len(py_code))  # 1 block
        
        res = self.__do_encrypt_decrypt_file(py_code)
        self.assertEqual(py_code, res)

    def test_process_py_code_less_1_block(self):
        py_code = b'v=123456789'
        self.assertLess(len(py_code), 16)  # less than 1 block
        
        res = self.__do_encrypt_decrypt_file(py_code)
        self.assertEqual(py_code, res)

    def test_process_py_code_2_block(self):
        py_code = b'v1=12345678901\r\n'
        py_code += b'v2=12345678901\r\n'
        self.assertEqual(len(py_code), 32)  # 2 blocks
        
        res = self.__do_encrypt_decrypt_file(py_code)
        self.assertEqual(py_code, res)

if __name__ == '__main__':
    unittest.main()
