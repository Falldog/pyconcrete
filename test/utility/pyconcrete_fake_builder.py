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

import importlib
import shutil
import sys
import tempfile
from os.path import join
from unittest.mock import patch

from .defines import ROOT_DIR
from .shell_tools import touch

# change the name of pyconcrete parent dir, avoid testing to do import as usual
TMP_BASE_PACKAGE_NAME = 'src_in_tmp_fake'


def import_pyconcrete_in_test():
    """
    Don't import pyconcrete directly. Avoid to import pyconcrete from code repository to keep the testing code clear.
    So, in testing environment, we should import pyconcrete via this function.
    """
    global fake_pyconcrete_in_test_builder

    m = importlib.import_module(f'{TMP_BASE_PACKAGE_NAME}.pyconcrete')
    return m


def get_pyconcrete_imported_obj(obj_name):
    module = import_pyconcrete_in_test()
    return getattr(module, obj_name)


class FakePyconcreteInTestBuilder:
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

    @property
    def pyconcrete_path(self):
        return join(self.tmp_pyconcrete_base_path, TMP_BASE_PACKAGE_NAME)

    def init(self):
        if self.is_init:
            return self.tmp_pyconcrete_base_path

        tmp_dir = tempfile.mkdtemp(prefix='pyconcrete_lib_')
        tmp_src_dir = join(tmp_dir, TMP_BASE_PACKAGE_NAME)

        shutil.copytree(join(ROOT_DIR, 'src'), tmp_src_dir)
        touch(join(tmp_dir, '__init__.py'))
        touch(join(tmp_src_dir, '__init__.py'))
        self.tmp_pyconcrete_base_path = tmp_dir

        self.is_init = True
        self._add_sys_path()
        return self.tmp_pyconcrete_base_path

    def destroy(self):
        if self.is_init:
            shutil.rmtree(self.tmp_pyconcrete_base_path)
            self._remove_sys_path()
            self.tmp_pyconcrete_base_path = None
            self.is_init = False

    @staticmethod
    def patch(pyconcrete_obj: str, *args, **kwargs):
        assert pyconcrete_obj.startswith('pyconcrete')
        return patch(f'{TMP_BASE_PACKAGE_NAME}.{pyconcrete_obj}', *args, **kwargs)

    def _add_sys_path(self):
        sys.path.insert(0, self.tmp_pyconcrete_base_path)

    def _remove_sys_path(self):
        try:
            sys.path.remove(self.tmp_pyconcrete_base_path)
        except ValueError:
            pass


# singleton
fake_pyconcrete_in_test_builder = FakePyconcreteInTestBuilder()

# for patch behavior working. we should call init() at the beginning, otherwise it will raise exception when patching
# testing function like below sample code.
# ```
# @builder.patch('pyconcrete.decrypt_buffer')
# def test_import(self, ...):
#     ...
# ```
fake_pyconcrete_in_test_builder.init()
