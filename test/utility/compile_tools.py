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

import subprocess
import sys
from os.path import join

from .defines import ROOT_DIR
from .pyconcrete_builder import get_pyconcrete_env_path


def lib_compile_pyc(folder, remove_py=False):
    admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
    arg_remove_py = '--remove-py' if remove_py else ''
    subprocess.check_call(
        '%s %s compile --source=%s --pyc %s' % (sys.executable, admin_path, folder, arg_remove_py),
        env=get_pyconcrete_env_path(),
        shell=True,
    )


def lib_compile_pye(folder, remove_py=False, remove_pyc=False):
    admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
    arg_remove_py = '--remove-py' if remove_py else ''
    arg_remove_pyc = '--remove-pyc' if remove_pyc else ''
    subprocess.check_call(
        '%s %s compile --source=%s --pye %s %s' % (sys.executable, admin_path, folder, arg_remove_py, arg_remove_pyc),
        env=get_pyconcrete_env_path(),
        shell=True,
    )
