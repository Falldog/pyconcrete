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

import imp
import os
import shutil
import subprocess
import tempfile
from os.path import basename, isdir, join

from .compile_tools import lib_compile_pye

SOURCE_DIR_NAME = 'src'
MODULE_PREFIX = 'test_'

MAIN_PY = 'main.py'
MAIN_PYE = 'main.pye'
VALIDATOR_PY = 'validator.py'


class ImportedTestCaseError(Exception):
    def __init__(self, output_lines, return_code, validate_errors, *args, **kwargs):
        self.output_lines = output_lines
        self.return_code = return_code
        self.validate_errors = validate_errors


class ImportedTestCase(object):
    def __init__(self, pyconcrete_exe, module_path):
        self.pyconcrete_exe = pyconcrete_exe
        self.module_path = module_path
        self.tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_testcase_')

    def close(self):
        shutil.rmtree(self.tmp_dir)

    @property
    def module_name(self):
        return basename(self.module_path)

    @property
    def module_src_path(self):
        return join(self.module_path, SOURCE_DIR_NAME)

    def is_available_test_case(self):
        if not isdir(self.module_path):
            return False
        if not self.module_name.startswith(MODULE_PREFIX):
            return False

        module_files = os.listdir(self.module_path)
        if VALIDATOR_PY not in module_files:
            return False
        if SOURCE_DIR_NAME not in module_files:
            return False

        module_code_files = os.listdir(self.module_src_path)
        if MAIN_PY not in module_code_files:
            return False

        return True

    def run(self):
        main_pye_path = self.build_pye()
        ret_data = self.execute(main_pye_path)
        return self.validate(ret_data, main_pye_path)

    def build_pye(self):
        dest_dir = join(self.tmp_dir, self.module_name)
        shutil.copytree(self.module_src_path, dest_dir)

        lib_compile_pye(dest_dir, remove_py=True, remove_pyc=True)
        return join(dest_dir, 'main.pye')

    def execute(self, main_pye_path):
        p = subprocess.Popen(
            [self.pyconcrete_exe, main_pye_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output, error = p.communicate()
        output = output.decode('utf8')
        output = output.replace('\r\n', '\n')
        return {
            'output_lines': output.strip().split('\n'),
            'return_code': p.returncode,
        }

    def validate(self, ret_data, main_pye_path):
        validator_py = join(self.module_path, VALIDATOR_PY)
        validator = imp.load_source('', validator_py)
        try:
            return validator.validate(
                ret_data['output_lines'],
                main_pye_path=main_pye_path,
                return_code=ret_data['return_code'],
            )
        except Exception as e:
            raise ImportedTestCaseError(ret_data['output_lines'], ret_data['return_code'], str(e))
