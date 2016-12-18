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

import sys
import base
import shutil
from os.path import join


class TestImportHook(base.TestPyConcreteBase):
    def test_py_import_hook(self):
        import os
        assert os
        import csv
        assert csv

    def test_py_relative_import(self):
        import os
        sys.path.insert(0, os.path.join(base.ROOT_DIR, 'test', 'data'))
        from test.data.relative_import import main
        self.assertEqual(main.data, 'main')
        self.assertEqual(main.util.data, 'util')
        sys.path.pop(0)

    def test_pye_relative_import(self):
        src_path = join(base.ROOT_DIR, 'test', 'data', 'relative_import')
        shutil.copytree(src_path, join(self.tmp_dir, 'relative_import'))
        base.touch(join(self.tmp_dir, '__init__.py'))

        self.lib_compile_pye(self.tmp_dir, remove_py=True, remove_pyc=True)

        from relative_import import main
        self.assertEqual(main.data, 'main')
        self.assertEqual(main.util.data, 'util')


