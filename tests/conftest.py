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
    def __init__(self, env_dir, pyconcrete_ext=None, install_mode='exe', install_cli=False):
        assert install_mode in ('lib', 'exe')
        self.executable = None
        self.bin_dir = None
        self.env_dir = env_dir
        self._pyconcrete_ext = pyconcrete_ext
        self._install_mode = install_mode
        self._install_cli = install_cli
        self.create()

    def create(self):
        subprocess.check_call([sys.executable, '-m', 'virtualenv', self.env_dir])
        self.bin_dir = join(self.env_dir, 'bin')
        self.executable = join(self.bin_dir, 'python')
        self._ensure_pyconcrete_exist()

    def python(self, *args: [str], shell=False):
        cmd = [self.executable, *args]
        if shell:
            cmd = ' '.join(cmd)
        return subprocess.check_output(cmd, shell=shell).decode()

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
        cli = join(self.bin_dir, 'pyecli')
        return subprocess.check_output([cli, *args]).decode()

    def _ensure_pyconcrete_exist(self):
        proc = subprocess.run(f'{self.executable} -m pip list | grep -c pyconcrete', shell=True)
        pyconcrete_exist = bool(proc.returncode == 0)
        if not pyconcrete_exist:
            args = [
                'install',
                f'--config-settings=setup-args=-Dpassphrase={PASSPHRASE}',
                f'--config-settings=setup-args=-Dext={self._pyconcrete_ext}' if self._pyconcrete_ext else '',
                f'--config-settings=setup-args=-Dmode={self._install_mode}',
                f'--config-settings=setup-args=-Dinstall-cli={"true" if self._install_cli else "false"}',
                '--quiet',
                ROOT_DIR,
            ]
            args = [arg for arg in args if arg]  # filter empty string
            self.pip(*args)


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
def pye_cli(venv_cli: Venv):
    return PyeCli(venv_cli)


@pytest.fixture(scope='session')
def venv_exe(tmp_path_factory):
    """
    the virtual environment for testing pyconcrete exe
    """
    return Venv(
        env_dir=tmp_path_factory.mktemp('venv_exe_'),
    )


@pytest.fixture(scope='session')
def venv_cli(tmp_path_factory):
    """
    the virtual environment for testing pyconcrete cli
    """
    return Venv(
        env_dir=tmp_path_factory.mktemp('venv_cli_'),
        install_cli=True,
    )


@pytest.fixture(scope='session')
def venv_lib(tmp_path_factory):
    """
    the virtual environment for testing pyconcrete lib
    """
    return Venv(
        env_dir=tmp_path_factory.mktemp('venv_lib_'),
        install_mode='lib',
    )


@pytest.fixture
def sample_module_path():
    return join(ROOT_DIR, 'tests', 'fixtures', 'sample_module')


@pytest.fixture
def sample_import_sub_module_path():
    return join(ROOT_DIR, 'tests', 'exe_testcases', 'test_import_sub_module')
