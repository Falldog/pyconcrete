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
import imp
import marshal
from os.path import join, exists, isdir

EXT_PY  = '.py'
EXT_PYC = '.pyc'
EXT_PYD = '.pyd'
EXT_PYE = '.pye'

__all__ = ["info"]

from . import _pyconcrete

info = _pyconcrete.info
encrypt_file = _pyconcrete.encrypt_file
decrypt_file = _pyconcrete.decrypt_file
decrypt_buffer = _pyconcrete.decrypt_buffer


class PyeLoader(object):
    def __init__(self, is_pkg, pkg_path, full_path):
        self.is_pkg = is_pkg
        self.pkg_path = pkg_path
        self.full_path = full_path
        with open(full_path, 'rb') as f:
            self.data = f.read()

    def new_module(self, fullname, path, package_path):
        m = imp.new_module(fullname)
        m.__file__ = path
        m.__loader__ = self
        if self.is_pkg:
            m.__path__ = [package_path]

        if "__name__" not in m.__dict__:
            m.__name__ = fullname

        return m

    def load_module(self, fullname):
        if fullname in sys.modules:  # skip reload by now ...
            return sys.modules[fullname]

        data = decrypt_buffer(self.data)  # decrypt pye
        
        if sys.version_info >= (3, 3):
            # reference python source code
            # python/Lib/importlib/_bootstrap_external.py _code_to_bytecode()
            magic = 12
        else:
            # load pyc from memory
            # reference http://stackoverflow.com/questions/1830727/how-to-load-compiled-python-modules-from-memory
            magic = 8

        code = marshal.loads(data[magic:])

        m = self.new_module(fullname, self.full_path, self.pkg_path)
        sys.modules[fullname] = m
        exec(code, m.__dict__)
        return m


class PyeMetaPathFinder(object):
    def find_module(self, fullname, path=None):
        mod_name = fullname.split('.')[-1]
        paths = path if path else sys.path

        for trypath in paths:
            mod_path = join(trypath, mod_name)
            is_pkg = isdir(mod_path)
            if is_pkg:
                full_path = join(mod_path, '__init__' + EXT_PYE)
                pkg_path = mod_path
            else:
                full_path = mod_path + EXT_PYE
                pkg_path = trypath

            if exists(full_path):
                return PyeLoader(is_pkg, pkg_path, full_path)


sys.meta_path.insert(0, PyeMetaPathFinder())

