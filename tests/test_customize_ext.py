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
from os.path import exists, join

import pytest

from .conftest import Venv


@pytest.mark.parametrize(
    "ext",
    [".pye", ".t", ".tw"],
)
def test_customize_ext(tmp_path_factory, tmpdir, sample_import_sub_module_path, ext):
    """build the standalone virtualenv for different file extensions"""
    # prepare
    target_dir = join(tmpdir, 'for_ext_module')
    main_encrypted = join(target_dir, f'main{ext}')
    venv = Venv(
        env_dir=tmp_path_factory.mktemp('venv_ext_'),
        pyconcrete_ext=ext,
        install_cli=True,
    )

    # compile to customized extension
    shutil.copytree(sample_import_sub_module_path, target_dir)
    venv.pyconcrete_cli(
        'compile',
        f'--ext={ext}',
        f'--source={target_dir}',
        '--pye',
        '--remove-py',
    )

    # verification (before)
    assert exists(main_encrypted) is True

    # execution
    output = venv.pyconcrete(main_encrypted)

    # verification (after)
    assert output == f'bar{os.linesep}'
