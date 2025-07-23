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
from os.path import join
from subprocess import CalledProcessError

import pytest

from .conftest import Venv


def test_install__without_cli(tmp_path_factory):
    venv = Venv(
        env_dir=tmp_path_factory.mktemp('venv_test_wo_cli'),
        install_cli=False,
    )
    cli_path = join(venv.bin_dir, 'pyecli')
    assert not os.path.exists(cli_path)


def test_install__mode_exe(venv_exe):
    # only exe exist
    assert os.path.exists(venv_exe.pyconcrete_exe)
    # lib should not exist, import should get failure
    with pytest.raises(CalledProcessError):
        venv_exe.python('-c', '"import pyconcrete"', shell=True)


def test_install__mode_lib(venv_lib):
    # only lib exist, exe should not be found
    assert not os.path.exists(venv_lib.pyconcrete_exe)
    # import should be success
    venv_lib.python('-c', '"import pyconcrete"', shell=True)
