#!/usr/bin/env python
# -*- coding: utf8 -*-
# Create on : 2019/07/13
from __future__ import unicode_literals

import os
from os.path import join

from test import base
from test.utility import ImportedTestCase, ImportedTestCaseError


MAIN_PY = 'main.py'
CODE_DIR = 'code'
VALIDATOR_PY = 'validator.py'


class TestThreading(base.TestPyConcreteBase):
    def discover(self):
        test_cases = []
        test_case_dir = join(base.ROOT_DIR, 'test', 'exe_testcases')
        for d in os.listdir(test_case_dir):
            test_case_path = join(test_case_dir, d)
            itc = ImportedTestCase(self._pyconcrete_exe, test_case_path)
            if itc.is_available_test_case():
                test_cases.append(itc)
            else:
                print('test_exe_testcases - {itc.module_name} (skip)'.format(itc=itc))
        return sorted(test_cases, key=lambda x: x.module_name)

    def test_auto_loading(self):
        test_cases = self.discover()
        for tc in test_cases:
            print('test_exe_testcases - {tc.module_name} ... '.format(tc=tc),
                  end='')
            try:
                res = tc.run()
                if res:
                    self.assertTrue(res, "{tc.module_name} validate failed".format(tc=tc))
                    print('Success')
                else:
                    print('Fail')
            except ImportedTestCaseError as e:
                print('Exception')
                print('>>>>>>')
                print('{tc.module_name} tmp_dir=`{tc.tmp_dir}`'.format(tc=tc))
                print('======= output lines ======')
                print('\n'.join(e.output_lines))
                print('======= validate_errors ======')
                print(e.validate_errors)
                print('<<<<<<')
            except:
                print('Exception')
                print('>>>>>>')
                print('{tc.module_name} tmp_dir=`{tc.tmp_dir}`'.format(tc=tc))
                print('<<<<<<')
                raise
            tc.close()

