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
from os.path import join
from unittest.mock import patch

from .defines import ROOT_DIR

TMP_BASE_PACKAGE_NAME = 'src'


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


class FakePyconcreteInTestForDebugBuilder:
    """
    Singleton instance
    For debug only. It will load the repo source directly for easily debug at IDE.
    """

    def __init__(self):
        self.tmp_pyconcrete_base_path = ROOT_DIR

    @property
    def pyconcrete_path(self):
        return join(self.tmp_pyconcrete_base_path, TMP_BASE_PACKAGE_NAME)

    def init(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def patch(pyconcrete_obj: str, *args, **kwargs):
        assert pyconcrete_obj.startswith('pyconcrete')
        return patch(f'{TMP_BASE_PACKAGE_NAME}.{pyconcrete_obj}', *args, **kwargs)


# singleton
fake_pyconcrete_in_test_builder = FakePyconcreteInTestForDebugBuilder()
