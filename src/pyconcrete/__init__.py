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
import sys
import imp
import string
import marshal
import __builtin__
from os.path import join, exists, isdir

EXT_PY  = '.py'
EXT_PYC = '.pyc'
EXT_PYD = '.pyd'
EXT_PYE = '.pye'

__all__ = ["info"]

import _pyconcrete

info = _pyconcrete.info
encrypt_file = _pyconcrete.encrypt_file
decrypt_file = _pyconcrete.decrypt_file
decrypt_buffer = _pyconcrete.decrypt_buffer


class LoaderBase(object):
    def __init__(self, is_package, *data):
        self.is_package = is_package
        self.data = data  # package_path, path, codestring
        
    def new_module(self, fullname, path, package_path):
        m = imp.new_module(fullname)
        m.__file__ = path
        if self.is_package:
            m.__path__ = [ package_path ]
        if "__name__" not in m.__dict__:
            m.__name__ = fullname
        m.__loader__ = self
        return m
        
class DefaultLoader(object):
    def __init__(self, is_package, *data):
        self.data = data

    def load_module(self, fullname):
        if fullname in sys.modules:  # skip reload by now ...
            return sys.modules[fullname]
        m = imp.load_module(fullname, *self.data)
        sys.modules[fullname] = m
        return m

class PyLoader(LoaderBase):
    def load_module(self, fullname):
        if fullname in sys.modules:  # skip reload by now ...
            return sys.modules[fullname]

        package_path, path, codestring = self.data
        #codestring = string.replace(codestring, '\r\n', '\n')

        if codestring and codestring[-1] != '\n':
            codestring += '\n'
        try:
            codeobject = __builtin__.compile(codestring, path, 'exec')
        except Exception, err:
            return None

        code = codeobject
        m = self.new_module(fullname, path, package_path)
        sys.modules[fullname] = m
        exec code in m.__dict__
        return m
        
class PyeLoader(LoaderBase):
    def load_module(self, fullname):
        if fullname in sys.modules:  # skip reload by now ...
            return sys.modules[fullname]
        package_path, path, img = self.data
        
        img = decrypt_buffer(img)  # decrypt pye
        
        # load pyc from memory, reference http://stackoverflow.com/questions/1830727/how-to-load-compiled-python-modules-from-memory
        code = marshal.loads(img[8:])

        m = self.new_module(fullname, path, package_path)
        sys.modules[fullname] = m
        exec code in m.__dict__
        return m
        
class ModuleImportHooker:
    def __init__(self, path):
        if not isdir(path):
            raise ImportError
        self.path = path

    def find_module(self, fullname, path=None):
        subname = fullname.split('.')[-1]

        fullpath = join(self.path, subname)
        maybe_pkg = isdir(fullpath)
        
        try:
            # pye file
            trypath = fullpath + EXT_PYE
            if exists(trypath):
                img = file(trypath, 'rb').read()
                return PyeLoader(False, self.path, trypath, img)
            
            # package
            trypath = join(fullpath, '__init__' + EXT_PYE)
            if maybe_pkg and exists(trypath):
                img = file(trypath, 'rb').read()
                return PyeLoader(True, fullpath, trypath, img)

            path = self.path and [self.path] or path

            find = False
            if maybe_pkg:
                for suffix, mode, type in imp.get_suffixes():
                    p = join(path[0], subname, '__init__' + suffix)
                    if exists(p):
                        find = True
                        break
            if not find:
                for suffix, mode, type in imp.get_suffixes():
                    p = join(path[0], subname + suffix)
                    if exists(p):
                        find = True
                        break
            if find:
                data = imp.find_module(subname, path)
                return DefaultLoader(False, *data)
            else:
                return None
            
        except ImportError:
            return None


sys.path_hooks.insert(0, ModuleImportHooker)
sys.path_importer_cache.clear()
