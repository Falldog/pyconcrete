#/usr/bin/env python
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
    def __init__(self):
        pass

    def find_module(self, fullname, path=None):
        subname = fullname.split('.')[-1]

        pathlist = sys.path
        if path:
            pathlist = path

        for onepath in pathlist:
            fullpath = join(onepath, subname)
            maybe_pkg = isdir(fullpath)

            
            try:
                # pye file
                trypath = fullpath + EXT_PYE
                if exists(trypath):
                    img = file(trypath, 'rb').read()
                    return PyeLoader(False, onepath, trypath, img)
                
            except ImportError:
                pass
        

        return None


sys.meta_path.append(ModuleImportHooker())
