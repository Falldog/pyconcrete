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
from os.path import join

import pytest

from .shell_tools import touch

YES = 'yes'
NO = 'no'


def test_cli__encrypt_single_file(venv, pye_cli, tmpdir, sample_module_path):
    # prepare
    source_file = join(tmpdir, 'm.py')
    encrypt_file = join(tmpdir, 'm.pye')

    with open(source_file, 'w') as f:
        f.write("""print('hello world')""")

    # execution
    venv.pyconcrete_cli('compile', f'--source={source_file}', '--pye')

    # validation
    assert os.path.exists(encrypt_file)


def test_cli__encrypt_whole_folder(venv, pye_cli, tmpdir, sample_module_path):
    # prepare
    source_dir = join(tmpdir, 'sample_module')
    shutil.copytree(sample_module_path, source_dir)

    # execution
    venv.pyconcrete_cli('compile', f'--source={source_dir}', '--pye')

    # validation
    for root, dirs, files in os.walk(sample_module_path):
        for filename in files:
            source_file = str(join(root, filename))
            source_relative_path = os.path.relpath(source_file, sample_module_path)
            py_file = join(source_dir, source_relative_path)
            pye_file = py_file + 'e'
            assert os.path.exists(pye_file)


_f_main = 'main.pye'
_f_ri__main = join('relative_import', 'main.pye')
_f_ri__util = join('relative_import', 'util.pye')


@pytest.mark.parametrize(
    "pattern,expect_result_map",
    [
        (None, {_f_main: YES, _f_ri__main: YES, _f_ri__util: YES}),
        ("main.py", {_f_main: NO, _f_ri__main: NO, _f_ri__util: YES}),
        ("relative_import/*", {_f_main: YES, _f_ri__main: NO, _f_ri__util: NO}),
        ("relative_import/util.py", {_f_main: YES, _f_ri__main: YES, _f_ri__util: NO}),
        ("relative_import/main.py", {_f_main: YES, _f_ri__main: NO, _f_ri__util: YES}),
        ("main.py util.py", {_f_main: NO, _f_ri__main: NO, _f_ri__util: NO}),
    ],
)
def test_cli__ignore_rule__in_deep_folder(venv, tmpdir, sample_module_path, pattern, expect_result_map):
    # prepare
    source_dir = join(tmpdir, 'sample_module')
    shutil.copytree(sample_module_path, source_dir)

    # execution
    ignore_args = []
    if pattern is not None:
        ignore_args.append('-i')
        ignore_args.extend(pattern.split(' '))
    venv.pyconcrete_cli('compile', f'--source={source_dir}', '--pye', *ignore_args)

    # validation
    for f, encrypted in expect_result_map.items():
        if encrypted == YES:
            path = join(source_dir, f)
            assert os.path.exists(path), f"ignore pattern `{pattern}` fail on exist file `{f}` validation!"
        else:  # encrypted == NO
            path = join(source_dir, f)
            assert not os.path.exists(path), f"ignore pattern `{pattern}` fail on non-exist file `{f}` validation!"


_f_foo = 'foo.pye'
_f_test1 = join('test1.pye')
_f_test2 = join('test2.pye')
_f_test3 = join('test3.pye')
_f_test = join('test.pye')
_f_a_test = join('a_test.pye')
_f_b_test = join('b_test.pye')


@pytest.mark.parametrize(
    "pattern,expect_result_map",
    [
        (
            None,
            {_f_foo: YES, _f_test1: YES, _f_test2: YES, _f_test3: YES, _f_test: YES, _f_a_test: YES, _f_b_test: YES},
        ),
        (
            "*/test.py",
            {_f_foo: YES, _f_test1: YES, _f_test2: YES, _f_test3: YES, _f_test: NO, _f_a_test: YES, _f_b_test: YES},
        ),
        (
            "/test.py",
            {_f_foo: YES, _f_test1: YES, _f_test2: YES, _f_test3: YES, _f_test: NO, _f_a_test: YES, _f_b_test: YES},
        ),
        (
            "test.py",
            {_f_foo: YES, _f_test1: YES, _f_test2: YES, _f_test3: YES, _f_test: NO, _f_a_test: YES, _f_b_test: YES},
        ),
        (
            "test?.py",
            {_f_foo: YES, _f_test1: NO, _f_test2: NO, _f_test3: NO, _f_test: YES, _f_a_test: YES, _f_b_test: YES},
        ),
        (
            "test[1,3].py",
            {_f_foo: YES, _f_test1: NO, _f_test2: YES, _f_test3: NO, _f_test: YES, _f_a_test: YES, _f_b_test: YES},
        ),
        (
            "test[!1,3].py",
            {_f_foo: YES, _f_test1: YES, _f_test2: NO, _f_test3: YES, _f_test: YES, _f_a_test: YES, _f_b_test: YES},
        ),
    ],
)
def test_cli__ignore_rule__in_same_folder(venv, pye_cli, tmpdir, pattern, expect_result_map):
    # prepare
    source_dir = tmpdir
    # create the files which list on parametrize
    for f, encrypted in expect_result_map.items():
        name, ext = os.path.splitext(f)
        py_file = join(source_dir, f'{name}.py')
        touch(py_file)

    # execution
    ignore_args = []
    if pattern is not None:
        ignore_args.append('-i')
        ignore_args.extend(pattern.split(' '))
    venv.pyconcrete_cli('compile', f'--source={source_dir}', '--pye', *ignore_args)

    # validation
    for f, encrypted in expect_result_map.items():
        if encrypted == YES:
            path = join(source_dir, f)
            assert os.path.exists(path), f"ignore pattern `{pattern}` fail on exist file `{f}` validation!"
        else:  # encrypted == NO
            path = join(source_dir, f)
            assert not os.path.exists(path), f"ignore pattern `{pattern}` fail on non-exist file `{f}` validation!"
