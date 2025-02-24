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
import sys
from os.path import abspath, dirname, join

import pytest

ROOT_DIR = abspath(join(dirname(__file__), '..'))
PASSPHRASE = 'TestPyconcrete'


class Venv:
    def __init__(self, env_dir):
        self.executable = None
        self.bin_dir = None
        self.env_dir = env_dir
        self.create()

    def create(self):
        subprocess.check_call([sys.executable, '-m', 'virtualenv', self.env_dir])
        self.bin_dir = join(self.env_dir, 'bin')
        self.executable = join(self.bin_dir, 'python')
        self._ensure_pyconcrete_exist()

    def python(self, *args: [str]):
        return subprocess.check_output([self.executable, *args]).decode()

    def pip(self, *args: [str]):
        return self.python('-m', 'pip', *args)

    @property
    def pyconcrete_exe(self):
        self._ensure_pyconcrete_exist()
        return join(self.bin_dir, 'pyconcrete')

    def pyconcrete(self, *args: [str]):
        self._ensure_pyconcrete_exist()
        return subprocess.check_output([self.pyconcrete_exe, *args]).decode()

    def pyconcrete_cli(self, *args: [str]):
        self._ensure_pyconcrete_exist()
        cli_script = join(ROOT_DIR, 'pyecli')
        return subprocess.check_output([self.executable, cli_script, *args]).decode()

    def _ensure_pyconcrete_exist(self):
        proc = subprocess.run(f'{self.executable} -m pip list | grep -c pyconcrete', shell=True)
        pyconcrete_exist = bool(proc.returncode == 0)
        if not pyconcrete_exist:
            self.pip(
                'install',
                f'--config-settings=setup-args=-Dpassphrase={PASSPHRASE}',
                '--quiet',
                ROOT_DIR,
            )


class PyeCli:
    def __init__(self, venv: Venv):
        self._venv = venv
        self._tmp_dir = None
        self._module_name = None
        self._source_code = None

    def setup(self, tmp_dir, module_name):
        self._tmp_dir = tmp_dir
        self._module_name = module_name
        return self

    @property
    def tmp_dir(self):
        """tmp dir to do the encryption"""
        return self._tmp_dir

    def source_code(self, code):
        self._source_code = code
        return self

    def get_encrypt_path(self):
        assert self._module_name
        assert self._source_code

        py_module_path = join(self._tmp_dir, f'{self._module_name}.py')
        pye_module_path = join(self._tmp_dir, f'{self._module_name}.pye')
        with open(py_module_path, 'w') as f:
            f.write(self._source_code)

        self._venv.pyconcrete_cli('compile', '--remove-py', '--pye', '-s', py_module_path)

        return pye_module_path


@pytest.fixture
def pye_cli(venv: Venv):
    return PyeCli(venv)


@pytest.fixture(scope='session')
def venv(tmp_path_factory):
    return Venv(tmp_path_factory.mktemp('venv_'))


@pytest.fixture
def sample_module_path():
    return join(ROOT_DIR, 'tests', 'fixtures', 'sample_module')
