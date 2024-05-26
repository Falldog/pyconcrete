#!/usr/bin/env python
#
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

import atexit
import os
import re
import shutil
import subprocess
import sys
import tempfile
from os.path import exists, join

from src.config import SECRET_HEADER_PATH

from .defines import ROOT_DIR

PASSPHRASE = 'TEST'


def copy_pyconcrete_ext(tmp_dir):
    tmp_pyconcrete = join(tmp_dir, 'pyconcrete')
    for f in os.listdir(tmp_pyconcrete):
        if re.match(r'^_pyconcrete.*\.(so|dll|pyd)$', f):
            shutil.copy(join(tmp_pyconcrete, f), join(ROOT_DIR, 'src', 'pyconcrete'))
            break


def get_pyconcrete_env_path():
    """
    append tmp_pyconcrete_dir path into PYTHONPATH
    for subprocess execute script and import the pyconcrete we just builded
    """
    global pyconcrete_in_test_builder
    path = pyconcrete_in_test_builder.init()
    env = os.environ.copy()
    env.setdefault('PYTHONPATH', '')
    env['PYTHONPATH'] += os.pathsep + path
    return env


class PyconcreteInTestBuilder:
    """
    Singleton instance
    Build once, and reuse it to generate pye files. Destroy before end of process.
    """

    def __init__(self):
        self.is_init = False
        self.tmp_pyconcrete_dir = None
        self.tmp_pyconcrete_exe_path = None

    @property
    def pyconcrete_exe_path(self):
        return self.tmp_pyconcrete_exe_path

    def init(self):
        if self.is_init:
            return self.tmp_pyconcrete_dir

        # remove secret key header, for testing on generate secret-key file
        if os.path.exists(SECRET_HEADER_PATH):
            os.remove(SECRET_HEADER_PATH)

        tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_lib_')

        _ori_dir = os.getcwd()
        os.chdir(ROOT_DIR)
        try:
            # just build
            # force_option = '--force' if force else ''
            # subprocess.check_call('python setup.py build --passphrase=%s %s' % (passphrase, force_option), shell=True)

            cmd = (
                sys.executable,
                'setup.py',
                'install',
                '--passphrase=%s' % PASSPHRASE,
                '--install-base=%s' % tmp_dir,
                '--install-purelib=%s' % tmp_dir,
                '--install-platlib=%s' % tmp_dir,
                '--install-scripts=%s' % join(tmp_dir, 'scripts'),
                '--install-headers=%s' % join(tmp_dir, 'headers'),
                '--install-data=%s' % join(tmp_dir, 'data'),
                '--quiet',
            )
            subprocess.check_call(' '.join(cmd), shell=True)

            copy_pyconcrete_ext(tmp_dir)

            exe_name = 'pyconcrete.exe' if sys.platform == 'win32' else 'pyconcrete'
            self.tmp_pyconcrete_exe_path = join(tmp_dir, 'scripts', exe_name)
            self.tmp_pyconcrete_dir = tmp_dir
            print(f'PyconcreteInTestBuilder.init() build pyconcrete at {tmp_dir}')

            if not exists(self.tmp_pyconcrete_exe_path):
                raise ValueError("can't find pyconcrete exe!")

            self.is_init = True

        finally:
            os.chdir(_ori_dir)

        return self.tmp_pyconcrete_dir

    def destroy(self):
        if self.is_init:
            shutil.rmtree(self.tmp_pyconcrete_dir)
            print(f'PyconcreteInTestBuilder.destroy() remove pyconcrete at {self.tmp_pyconcrete_dir}')

            self.tmp_pyconcrete_dir = None
            self.tmp_pyconcrete_exe_path = None
            self.is_init = False


# singleton
pyconcrete_in_test_builder = PyconcreteInTestBuilder()


def destroy_pyconcrete():
    pyconcrete_in_test_builder.destroy()


atexit.register(destroy_pyconcrete)
