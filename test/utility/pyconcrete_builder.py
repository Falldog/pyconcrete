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
from .shell_tools import touch

PASSPHRASE = 'TEST'
TMP_BASE_PACKAGE_NAME = 'src_in_tmp'  # change the name of pyconcrete parent dir, avoid testing to do import as usual


def copy_pyconcrete_ext(tmp_src_dir):
    tmp_pyconcrete = join(tmp_src_dir, 'pyconcrete')
    for f in os.listdir(tmp_pyconcrete):
        if re.match(r'^_pyconcrete.*\.(so|dll|pyd)$', f):
            shutil.copy(join(tmp_pyconcrete, f), join(ROOT_DIR, 'src', 'pyconcrete'))
            break


def get_pyconcrete_env_path():
    """
    append tmp_pyconcrete_base_path path into PYTHONPATH
    for subprocess execute script and import the pyconcrete we just build
    and the subprocess able to do import pyconcrete directly as below sample code
    `import pyconcrete`
    """
    global pyconcrete_in_test_builder
    pyconcrete_in_test_builder.init()
    path = pyconcrete_in_test_builder.pyconcrete_path  # allow to import pyconcrete directly
    env = os.environ.copy()
    env.setdefault('PYTHONPATH', '')
    env['PYTHONPATH'] += os.pathsep + path
    return env


def import_pyconcrete_in_test():
    """
    Don't import pyconcrete directly. Avoid to import pyconcrete from code repository to keep the testing code clear.
    So, in testing environment, we should import pyconcrete via this function.
    """
    global pyconcrete_in_test_builder
    import importlib

    m = importlib.import_module(f'{TMP_BASE_PACKAGE_NAME}.pyconcrete')
    return m


class PyconcreteInTestBuilder:
    """
    Singleton instance
    Build once, and reuse it to generate pye files. Destroy before end of process.
    """

    def __init__(self):
        self.is_init = False

        """
        temp dir path, it will include pyconcrete as `{tmp_pyconcrete_base_path}/{TMP_BASE_PACKAGE_NAME}/pyconcrete`
        so, if we want to import pyconcrete, the import expression would as below pseudo code
        import `TMP_BASE_PACKAGE_NAME`.pyconcrete
        """
        self.tmp_pyconcrete_base_path = None

        self.tmp_pyconcrete_exe_path = None

    @property
    def pyconcrete_path(self):
        return join(self.tmp_pyconcrete_base_path, TMP_BASE_PACKAGE_NAME)

    @property
    def pyconcrete_exe_path(self):
        return self.tmp_pyconcrete_exe_path

    def init(self):
        if self.is_init:
            return self.tmp_pyconcrete_base_path

        # remove secret key header, for testing on generate secret-key file
        if os.path.exists(SECRET_HEADER_PATH):
            os.remove(SECRET_HEADER_PATH)

        ret = None

        tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_lib_')
        tmp_src_dir = join(tmp_dir, TMP_BASE_PACKAGE_NAME)
        os.makedirs(tmp_src_dir, exist_ok=True)
        touch(join(tmp_dir, '__init__.py'))
        touch(join(tmp_src_dir, '__init__.py'))

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
                '--install-base=%s' % tmp_src_dir,
                '--install-purelib=%s' % tmp_src_dir,
                '--install-platlib=%s' % tmp_src_dir,
                '--install-scripts=%s' % join(tmp_src_dir, 'scripts'),
                '--install-headers=%s' % join(tmp_src_dir, 'headers'),
                '--install-data=%s' % join(tmp_src_dir, 'data'),
                '--quiet',
            )
            subprocess.check_call(' '.join(cmd), shell=True)

            copy_pyconcrete_ext(tmp_src_dir)

            exe_name = 'pyconcrete.exe' if sys.platform == 'win32' else 'pyconcrete'
            self.tmp_pyconcrete_exe_path = join(tmp_src_dir, 'scripts', exe_name)
            self.tmp_pyconcrete_base_path = tmp_dir
            print(f'PyconcreteInTestBuilder.init() build pyconcrete at {self.tmp_pyconcrete_base_path}')

            if not exists(self.tmp_pyconcrete_exe_path):
                raise ValueError("can't find pyconcrete exe!")

            self.is_init = True
            ret = self.tmp_pyconcrete_base_path

        finally:
            os.chdir(_ori_dir)

        return ret

    def destroy(self):
        if self.is_init:
            shutil.rmtree(self.tmp_pyconcrete_base_path)
            print(f'PyconcreteInTestBuilder.destroy() remove pyconcrete at {self.tmp_pyconcrete_base_path}')

            self.tmp_pyconcrete_base_path = None
            self.tmp_pyconcrete_exe_path = None
            self.is_init = False


# singleton
pyconcrete_in_test_builder = PyconcreteInTestBuilder()


def destroy_pyconcrete():
    pyconcrete_in_test_builder.destroy()


atexit.register(destroy_pyconcrete)
