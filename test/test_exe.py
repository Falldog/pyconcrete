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

import os
import subprocess
from test import base


class TestPyconcreteExe(base.TestPyConcreteBase):
    def test_execute_pye(self):
        pye = self.lib_gen_pye('import os\n' 'print(os.getcwd())', pye_filename='main.pye')

        output = subprocess.check_output([self._pyconcrete_exe, pye])
        output = output.decode('utf8')
        self.assertEqual(output.strip(), os.getcwd())

    def test_execute_not_exist_file(self):
        output = subprocess.check_call([self._pyconcrete_exe, 'TheFileIsNotExists'])
        self.assertEqual(output, 0)

    def test_sys_path(self):
        """pye dir should be listed in sys.path"""
        pye = self.lib_gen_pye('import sys\n' 'paths = "\\n".join(sys.path)\n' 'print(paths)', pye_filename='main.pye')

        pye_dir = os.path.dirname(pye)
        pye_dir = os.path.realpath(pye_dir)  # tmpdir would be under symlink at MacOS

        output = subprocess.check_output([self._pyconcrete_exe, pye])
        output = output.decode('utf8')
        output = output.replace('\r\n', '\n')
        paths = output.split('\n')

        self.assertTrue(pye_dir in paths, "pye dir(%s) not in output paths %s" % (pye_dir, paths))

    def test_sys_argv(self):
        pye = self.lib_gen_pye('import sys\n' 'argv = " ".join(sys.argv)\n' 'print(argv)', pye_filename='main.pye')

        output = subprocess.check_output([self._pyconcrete_exe, pye])
        output = output.decode('utf8')
        self.assertEqual(output.strip(), pye)

    def test_sys_argv_more_arguments(self):
        pye = self.lib_gen_pye('import sys\n' 'argv = " ".join(sys.argv)\n' 'print(argv)', pye_filename='main.pye')

        output = subprocess.check_output([self._pyconcrete_exe, pye, '1', '2', '3'])
        output = output.decode('utf8')

        self.assertEqual(output.strip(), pye + ' 1 2 3')

    # def test_sys_exit(self):
    #     pye = self.lib_gen_pye('import sys\n'
    #                            'sys.exit(1)',
    #                            pye_filename='main.pye')
    #
    #     output = subprocess.call([self._pyconcrete_exe, pye])
    #     self.assertEqual(output, 1)

    def test__name__be__main__(self):
        pye = self.lib_gen_pye('print(__name__)', pye_filename='main.pye')

        output = subprocess.check_output([self._pyconcrete_exe, pye])
        output = output.decode('utf8')
        self.assertEqual(output.strip(), '__main__')
