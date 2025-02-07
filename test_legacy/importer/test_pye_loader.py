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
import unittest
from os.path import join

from test_legacy.utility.gen_code_tools import lib_gen_pyc
from test_legacy.utility.pyconcrete_fake_builder import fake_pyconcrete_in_test_builder as builder
from test_legacy.utility.pyconcrete_fake_builder import get_pyconcrete_imported_obj
from test_legacy.utility.str_tools import random_module_name


def gen_fake_pye(code, module_name, folder):
    """filename as .pye but content is .pyc"""
    pyc_path = lib_gen_pyc(code, f'{module_name}.pyc', folder)
    pye_path = join(folder, f'{module_name}.pye')
    shutil.move(pyc_path, pye_path)
    return pye_path


def fake_decrypt_buffer(data):
    return data


def unload_module(module_name):
    del sys.modules[module_name]


class TestPyeLoader(unittest.TestCase):
    """
    Inherit from unittest.TestCase rather than TestPyConcreteBase.
    Allow to run test in local dev environment without build pyconcrete.
    """

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp('_pyconcrete')
        sys.path.insert(0, self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)
        sys.path.remove(self.tmp_dir)

    @builder.patch('pyconcrete.decrypt_buffer', fake_decrypt_buffer)
    def test__loader__basic(self):
        PyeLoader = get_pyconcrete_imported_obj('PyeLoader')

        # prepare
        module_name = random_module_name()
        pye_full_path = gen_fake_pye('ver="1.0"', module_name, self.tmp_dir)

        expected__file__ = pye_full_path
        expected__name__ = module_name

        # load
        loader = PyeLoader(module_name, pye_full_path)
        module = loader.load_module(module_name)

        # validation
        self.assertEqual(module.__name__, expected__name__)
        self.assertEqual(module.__file__, expected__file__)
        self.assertTrue(isinstance(module.__loader__, PyeLoader))

        unload_module(module_name)

    @builder.patch('pyconcrete.decrypt_buffer', fake_decrypt_buffer)
    def test__import__basic(self):
        PyeLoader = get_pyconcrete_imported_obj('PyeLoader')

        # prepare
        module_name = random_module_name()
        pye_full_path = gen_fake_pye('ver="1.0"', module_name, self.tmp_dir)

        expected__file__ = pye_full_path
        expected__name__ = module_name

        # import
        module = importlib.import_module(module_name)

        # validation
        self.assertEqual(module.__name__, expected__name__)
        self.assertEqual(module.__file__, expected__file__)
        self.assertTrue(isinstance(module.__loader__, PyeLoader))

        unload_module(module_name)
