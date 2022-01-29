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

import os
import shutil
import subprocess
import sys
import unittest
from os.path import abspath, dirname, exists, join
from test import base

ROOT_DIR = abspath(join(dirname(__file__), '..'))
SAMPLE_PACKAGE_DIR = join(ROOT_DIR, 'test', 'data')


class TestAdminScript(base.TestPyConcreteBase):
    def setUp(self):
        super(TestAdminScript, self).setUp()
        self._ori_dir = os.getcwd()
        os.chdir(ROOT_DIR)

    def tearDown(self):
        super(TestAdminScript, self).tearDown()
        os.chdir(self._ori_dir)

    def test_parse_file(self):
        target_dir = join(self.tmp_dir, 'data')
        shutil.copytree(SAMPLE_PACKAGE_DIR, target_dir)
        target_file = join(target_dir, 'main.py')
        expect_file = join(target_dir, 'main.pye')

        subprocess.check_call(
            '%s pyconcrete-admin.py compile --source=%s --pye' % (sys.executable, target_file),
            env=base.get_pyconcrete_env_path(),
            shell=True,
        )

        self.assertTrue(exists(expect_file))

    def test_parse_folder(self):
        target_dir = join(self.tmp_dir, 'data')
        # print 'src=%s, target=%s' % (SAMPLE_PACKAGE_DIR, target_dir)
        shutil.copytree(SAMPLE_PACKAGE_DIR, target_dir)
        expect_file1 = join(target_dir, '__init__.pye')
        expect_file2 = join(target_dir, 'main.pye')

        subprocess.check_call(
            '%s pyconcrete-admin.py compile --source=%s --pye' % (sys.executable, target_dir),
            env=base.get_pyconcrete_env_path(),
            shell=True,
        )

        self.assertTrue(exists(expect_file1))
        self.assertTrue(exists(expect_file2))


class TestAdminIgnoreFilesScript(base.TestPyConcreteBase):
    def setUp(self):
        super(TestAdminIgnoreFilesScript, self).setUp()
        self.lib_gen_py("", "test1.py")
        self.lib_gen_py("", "test2.py")
        self.lib_gen_py("", "test.py")
        self.lib_gen_py("", "a_test.py")
        self.lib_gen_py("", "b_test.py")

    def test_ignore_file_list_match(self):
        target_dir = join(self.tmp_dir, 'data')
        relative_import_dir = join(self.tmp_dir, 'data', 'relative_import')
        shutil.copytree(SAMPLE_PACKAGE_DIR, target_dir)

        expect_file1 = join(target_dir, 'main.pye')
        # relative_import/util.pye
        expect_file2 = join(relative_import_dir, 'util.pye')
        # relative_import/main.pye
        expect_file3 = join(relative_import_dir, 'main.pye')

        subprocess.check_call(
            (
                '%s pyconcrete-admin.py compile --source=%s --pye -i relative_import/util.py'
                % (sys.executable, target_dir)
            ),
            env=base.get_pyconcrete_env_path(),
            shell=True,
        )

        self.assertTrue(exists(expect_file1))
        self.assertFalse(exists(expect_file2))
        self.assertTrue(exists(expect_file3))

    def test_ignore_file_list_match_everything(self):
        target_dir = join(self.tmp_dir, 'data')
        relative_import_dir = join(self.tmp_dir, 'data', 'relative_import')
        shutil.copytree(SAMPLE_PACKAGE_DIR, target_dir)

        expect_file1 = join(target_dir, 'main.pye')
        # relative_import/util.pye
        expect_file2 = join(relative_import_dir, 'util.pye')
        # relative_import/main.pye
        expect_file3 = join(relative_import_dir, 'main.pye')

        subprocess.check_call(
            ('%s pyconcrete-admin.py compile --source=%s --pye -i relative_import/*' % (sys.executable, target_dir)),
            env=base.get_pyconcrete_env_path(),
            shell=True,
        )

        self.assertTrue(exists(expect_file1))
        self.assertFalse(exists(expect_file2))
        self.assertFalse(exists(expect_file3))

    def test_ignore_file_list_match_everything_patterns(self):
        patterns = [
            "*%s%s" % (os.sep, "test.py"),  # */test.py
            "%s%s" % (os.sep, "test.py"),  # /test.py
            "test.py",  # test.py
        ]
        expect_file1 = join(self.tmp_dir, 'test1.pye')
        expect_file2 = join(self.tmp_dir, 'test2.pye')
        expect_file3 = join(self.tmp_dir, 'test.pye')
        expect_file4 = join(self.tmp_dir, 'a_test.pye')
        expect_file5 = join(self.tmp_dir, 'b_test.pye')

        def test_pattern(pat):
            subprocess.check_call(
                ('%s pyconcrete-admin.py compile --source=%s --pye -i "%s"' % (sys.executable, self.tmp_dir, pat)),
                env=base.get_pyconcrete_env_path(),
                shell=True,
            )

            msg = "pattern(%s) fail" % pat
            self.assertTrue(exists(expect_file1), msg)
            self.assertTrue(exists(expect_file2), msg)
            self.assertFalse(exists(expect_file3), msg)  # test.py excluded
            self.assertTrue(exists(expect_file4), msg)
            self.assertTrue(exists(expect_file5), msg)

        for pat in patterns:
            test_pattern(pat)

    def test_ignore_file_list_match_single(self):
        target_dir = join(self.tmp_dir, 'data')
        shutil.copytree(SAMPLE_PACKAGE_DIR, target_dir)

        expect_file1 = join(target_dir, '__init__.pye')
        expect_file2 = join(target_dir, 'main.pye')
        expect_file3 = join(self.tmp_dir, 'test1.pye')
        expect_file4 = join(self.tmp_dir, 'test2.pye')

        subprocess.check_call(
            ('%s pyconcrete-admin.py compile --source=%s --pye -i main.py test?.py' % (sys.executable, self.tmp_dir)),
            env=base.get_pyconcrete_env_path(),
            shell=True,
        )

        self.assertTrue(exists(expect_file1))
        self.assertFalse(exists(expect_file2))
        self.assertFalse(exists(expect_file3))
        self.assertFalse(exists(expect_file4))

    def test_ignore_file_list_match_in_seq(self):
        expect_file1 = join(self.tmp_dir, 'test1.pye')
        expect_file2 = join(self.tmp_dir, 'test2.pye')

        subprocess.check_call(
            (
                '%s pyconcrete-admin.py compile --source=%s --pye -i main.py test[1,3].py'
                % (sys.executable, self.tmp_dir)
            ),
            env=base.get_pyconcrete_env_path(),
            shell=True,
        )

        self.assertFalse(exists(expect_file1))
        self.assertTrue(exists(expect_file2))

    def test_ignore_file_list_match_not_in_seq(self):
        expect_file1 = join(self.tmp_dir, 'test1.pye')
        expect_file2 = join(self.tmp_dir, 'test2.pye')

        subprocess.check_call(
            (
                '%s pyconcrete-admin.py compile --source=%s --pye -i main.py test[!1,3].py'
                % (sys.executable, self.tmp_dir)
            ),
            env=base.get_pyconcrete_env_path(),
            shell=True,
        )

        self.assertTrue(exists(expect_file1))
        self.assertFalse(exists(expect_file2))


if __name__ == '__main__':
    unittest.main()
