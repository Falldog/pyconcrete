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


def test_lib__import_pyconcrete__venv_lib__validate__file__(venv_lib, pye_cli, tmpdir):
    """
    compare to test_exe__import_pyconcrete__venv_exe__validate__file__
    pyconcrete lib mode, the `pyconcrete` module contain`__file__` attribute
    """
    # prepare
    plain_src = """
import pyconcrete;
print(pyconcrete.__file__)
    """.strip()

    # execution
    output = venv_lib.python('-c', plain_src)
    output = output.strip()
    pyconcrete__file__ = output

    # verification
    assert pyconcrete__file__.startswith(str(venv_lib.env_dir))
