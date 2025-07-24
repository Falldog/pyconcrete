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
import subprocess
from dataclasses import dataclass
from os.path import basename, isdir, join

import pytest
import yaml

from .conftest import ROOT_DIR

TEST_CASES_DIR = join(ROOT_DIR, 'tests', 'exe_testcases')
MODULE_PREFIX = 'test_'
MAIN_PY = 'main.py'
MAIN_PYE = 'main.pye'
EXPECTED_YAML = 'expected.yaml'


@dataclass(frozen=True)
class ExpectedConfig:
    return_code: int
    stdout: str
    is_ignore_stdout: bool


def _is_valid_testcase_folder(sub_test_case_dir):
    module_path = sub_test_case_dir
    module_name = basename(module_path)

    if not isdir(module_path):
        return False
    if not module_name.startswith(MODULE_PREFIX):
        return False

    module_files = os.listdir(module_path)
    if (MAIN_PY not in module_files) or (EXPECTED_YAML not in module_files):
        return False

    return True


def _discover_exe_testcases_folder() -> list:
    test_cases = []
    for d in os.listdir(TEST_CASES_DIR):
        sub_test_case_dir = join(TEST_CASES_DIR, d)
        if _is_valid_testcase_folder(sub_test_case_dir):
            test_cases.append(sub_test_case_dir)
    return sorted(test_cases)


def _read_expected_yaml(expected_yaml: str) -> ExpectedConfig:
    with open(join(expected_yaml), 'r') as f:
        data = yaml.safe_load(f)

    expected = data['expected']
    config = ExpectedConfig(
        return_code=expected.get('return_code', 0),
        stdout=expected.get('stdout', '').replace('\n', os.linesep),
        is_ignore_stdout=expected.get('is_ignore_stdout', False),
    )
    return config


@pytest.mark.parametrize(
    "sub_test_case_folder",
    _discover_exe_testcases_folder(),
)
def test_exe__testcases(venv_cli, venv_exe, tmpdir, sub_test_case_folder: str):
    """
    Dynamic load testcases from tests/exe_testcases folder.

    Workflow process
    1. Copy files to tmp dir
    2. Encrypt .py to .pye
    3. Execute main.pye by pyconcrete
    4. Validate expected result by expected.yaml
    """
    # prepare
    dest_dir = join(tmpdir, basename(sub_test_case_folder))
    shutil.copytree(sub_test_case_folder, dest_dir)
    venv_cli.pyconcrete_cli('compile', f'--source={dest_dir}', '--pye', '--remove-py', '--remove-pyc')

    # execution
    main_pye = join(dest_dir, MAIN_PYE)
    p = subprocess.Popen(
        [venv_exe.pyconcrete_exe, main_pye],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output, error = p.communicate()
    output = output.decode()
    return_code = p.returncode

    # verification
    expected = _read_expected_yaml(join(dest_dir, EXPECTED_YAML))

    assert type(expected.return_code) is int, f"type of `return_code` ({type(expected.return_code)}) is not int"
    assert expected.return_code == return_code

    if not expected.is_ignore_stdout:
        assert type(expected.stdout) is str, f"type of `stdout` ({type(expected.stdout)}) is not string"
        assert expected.stdout == output
