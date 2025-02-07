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
from os.path import join

from test_legacy import base
from test_legacy.utility.defines import ROOT_DIR
from test_legacy.utility.imported_test_case import ImportedTestCase, ImportedTestCaseError
from test_legacy.utility.pyconcrete_builder import pyconcrete_in_test_builder


class TestExe(base.TestPyConcreteBase):
    def discover(self):
        test_cases = []
        test_case_dir = join(ROOT_DIR, 'test', 'exe_testcases')
        for d in os.listdir(test_case_dir):
            test_case_path = join(test_case_dir, d)
            itc = ImportedTestCase(pyconcrete_in_test_builder.pyconcrete_exe_path, test_case_path)
            if itc.is_available_test_case():
                test_cases.append(itc)
            else:
                itc.close()
                print('test_exe_testcases - {itc.module_name} (skip)'.format(itc=itc))
        return sorted(test_cases, key=lambda x: x.module_name)

    def test_auto_loading(self):
        test_cases = self.discover()
        error = False
        for tc in test_cases:
            print('test_exe_testcases - {tc.module_name} ... '.format(tc=tc), end='')
            try:
                res = tc.run()
                if res:
                    self.assertTrue(res, "{tc.module_name} validate failed".format(tc=tc))
                    print('Success')
                else:
                    print('Fail')
            except ImportedTestCaseError as e:
                print('Validate Exception')
                print('{{')
                print('  {tc.module_name} tmp_dir=`{tc.tmp_dir}`'.format(tc=tc))
                print('  return code = {return_code}'.format(return_code=e.return_code))
                print('  ======= output lines ======')
                print('  ' + '\n  '.join(e.output_lines))
                print('  ======= validate_errors ======')
                print('  ' + e.validate_errors)
                print('}}')
                error = True
            except Exception as e:
                print('Exception')
                print(str(e))
                print('{{')
                print('  {tc.module_name} tmp_dir=`{tc.tmp_dir}`'.format(tc=tc))
                print('}}')
                raise
            tc.close()

        assert error is False
