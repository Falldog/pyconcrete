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
import argparse
import py_compile
import pyconcrete
from os.path import join, exists, dirname, isdir

class PyConcreteAdmin(object):
    def __init__(self):
        self.parse_arg()
    
    def parse_arg(self):
        parser = argparse.ArgumentParser(description='PyConcreteAdmin.')
        parser.add_argument('build_pye', nargs='?', default=None,
                           help='parse specific folder and compile/encrypt whole py scripts')
        parser.add_argument('--recursive', action='store_false',
                           help='recursive process the folder')
        parser.add_argument('--verbose', action='store_true',
                           help='verbose mode')
        parser.add_argument('--ignore-list', nargs='*', default=None,
                           help='ignore file name list')
        self.args = parser.parse_args()
        print self.args
        idx = self.args.build_pye.find('=')
        self.args.build_pye = self.args.build_pye[idx+1:]
        print 'build_pye=%s' % self.args.build_pye
        print 'verbose=%s' % self.args.verbose
        print 'recursive=%s' % self.args.recursive
        
    def run(self):
        if self.args.build_pye:
            self.build_pye(self.args.build_pye)
        else:
            print 'please input correct command'
            
    def build_pye(self, folder):
        if not exists(folder):
            raise Exception("arg: build_pye, the folder doesn't exists (%s)" % folder)
        python_dir = dirname(sys.executable)
        if folder.startswith(python_dir):
            raise Exception("arg: build_pye, the folder should not under python dir(%s)" % folder)
        self.build_pye_dir(folder)
        
    def build_pye_dir(self, folder):
        print 'handle dir=%s' % folder
        for f in os.listdir(folder):
            if f in ['.', '..', '.git', '.svn']:
                continue
            fullpath = join(folder, f)
            if isdir(fullpath) and self.args.recursive:
                self.build_pye_dir(fullpath)
            elif fullpath.endswith('.py'):
                self.build_pye_file(fullpath)
                
    def build_pye_file(self, py_file):
        print 'handle file=%s' % py_file
        pyc_file = py_file + 'c'
        pye_file = py_file + 'e'
        pyc_exists = exists(pyc_file)
        if not pyc_exists or os.stat(py_file).st_mtime != os.stat(pyc_file).st_mtime:
            py_compile.compile(py_file)
        if not exists(pye_file) or os.stat(py_file).st_mtime != os.stat(pye_file).st_mtime:
            pyconcrete.encrypt_file(pyc_file, pye_file)
            if self.args.verbose:
                print '* create %s' % pye_file
        else:
            if self.args.verbose:
                print '* skip %s' % pye_file
        
        # .pyc doesn't exists at begining, remove it after .pye created
        if not pyc_exists:
            os.remove(pyc_file)
        
if __name__ == '__main__':
    admin = PyConcreteAdmin()
    admin.run()
