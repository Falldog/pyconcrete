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
import subprocess


def test_exe__execute_an_non_exist_file(venv):
    return_code = subprocess.call([venv.pyconcrete_exe, 'non_existing_file.txt'])
    assert return_code == 1


def test_exe__sys_path__should_contain_pye_file_dir(venv, pye_cli, tmpdir):
    # prepare
    pye_path = (
        pye_cli.setup(tmpdir, 'test_sys_path')
        .source_code(
            """
import sys
print('\\n'.join(sys.path))
            """.strip()
        )
        .get_encrypt_path()
    )

    # execution
    output = venv.pyconcrete(pye_path)
    output = output.replace('\r\n', '\n')
    paths = output.split('\n')
    pye_file_dir = pye_cli.tmp_dir

    # verification
    assert pye_file_dir in paths, "the folder of pye-file should be contained in sys.path"


def test_exe__sys_argv__first_arg_should_be_file_name(venv, pye_cli, tmpdir):
    # prepare
    pye_path = (
        pye_cli.setup(tmpdir, 'test_sys_argv')
        .source_code(
            """
import sys
print(" ".join(sys.argv))
            """.strip()
        )
        .get_encrypt_path()
    )

    # execution
    output = venv.pyconcrete(pye_path)
    output = output.strip()

    # verification
    assert output == pye_path


def test_exe__sys_argv__more_arguments(venv, pye_cli, tmpdir):
    # prepare
    pye_path = (
        pye_cli.setup(tmpdir, 'test_sys_argv')
        .source_code(
            """
import sys
print(" ".join(sys.argv))
            """.strip()
        )
        .get_encrypt_path()
    )

    # execution
    output = venv.pyconcrete(pye_path, '-a', '-b', '-c')
    output = output.strip()

    # verification
    assert output == f'{pye_path} -a -b -c'


def test_exe__import_pyconcrete__validate__file__(venv, pye_cli, tmpdir):
    # prepare
    pye_path = (
        pye_cli.setup(tmpdir, 'test_import_pyconcrete')
        .source_code(
            """
import pyconcrete
print(pyconcrete.__file__)
            """.strip()
        )
        .get_encrypt_path()
    )

    # execution
    output = venv.pyconcrete(pye_path)
    output = output.strip()
    pyconcrete__file__ = output

    # verification
    assert pyconcrete__file__.startswith(str(venv.env_dir))
