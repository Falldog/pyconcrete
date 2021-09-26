#!/usr/bin/env python
# -*- coding: utf8 -*-
# Create on : 2019/07/13
from __future__ import unicode_literals

import os
import sys
import imp
import shutil
import tempfile
import subprocess
from os.path import join, isdir, dirname, basename, abspath

ROOT_DIR = abspath(join(dirname(__file__), '..'))


SOURCE_DIR_NAME = 'src'
MODULE_PREFIX = 'test_'

MAIN_PY = 'main.py'
MAIN_PYE = 'main.pye'
VALIDATOR_PY = 'validator.py'


class ImportedTestCaseError(Exception):
    def __init__(self, output_lines, validate_errors, *args, **kwargs):
        self.output_lines = output_lines
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
        output_lines = self.execute(main_pye_path)
        return self.validate(output_lines, main_pye_path)

    def build_pye(self):
        dest_dir = join(self.tmp_dir, self.module_name)
        shutil.copytree(self.module_src_path, dest_dir)

        lib_compile_pye(dest_dir, remove_py=True, remove_pyc=True)
        return join(dest_dir, 'main.pye')

    def execute(self, main_pye_path):
        output = subprocess.check_output(
            [self.pyconcrete_exe, main_pye_path],
            stderr=subprocess.STDOUT,
        )
        output = output.decode('utf8')
        output = output.replace('\r\n', '\n')
        return output.strip().split('\n')

    def validate(self, output_lines, main_pye_path):
        validator_py = join(self.module_path, VALIDATOR_PY)
        validator = imp.load_source('', validator_py)
        try:
            return validator.validate(
                output_lines,
                main_pye_path=main_pye_path,
            )
        except Exception as e:
            import traceback
            raise ImportedTestCaseError(output_lines, str(e))


def lib_compile_pyc(folder, remove_py=False):
    from test.base import get_pyconcrete_env_path
    admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
    arg_remove_py = '--remove-py' if remove_py else ''
    subprocess.check_call(
        '%s %s compile --source=%s --pyc %s' % (sys.executable, admin_path, folder, arg_remove_py),
        env=get_pyconcrete_env_path(),
        shell=True,
    )


def lib_compile_pye(folder, remove_py=False, remove_pyc=False):
    from test.base import get_pyconcrete_env_path
    admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
    arg_remove_py = '--remove-py' if remove_py else ''
    arg_remove_pyc = '--remove-pyc' if remove_pyc else ''
    subprocess.check_call(
        '%s %s compile --source=%s --pye %s %s' % (sys.executable, admin_path, folder, arg_remove_py, arg_remove_pyc),
        env=get_pyconcrete_env_path(),
        shell=True,
    )


