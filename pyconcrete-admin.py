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
from os.path import join, exists, dirname, isdir, isfile

class PyConcreteError(Exception):
    pass

class PyConcreteAdmin(object):
    def __init__(self):
        self.parse_arg()
    
    def parse_arg(self):
        parser = argparse.ArgumentParser(description='PyConcreteAdmin.')
        parser.add_argument('cmd', 
                            default='', help='compile_pye|compile_all_pye')
        parser.add_argument('compile_all_pye', 
                            nargs='?', default=None, help='parse specific dir and compile/encrypt whole py scripts under the dir')
        parser.add_argument('--file', 
                            nargs=1, default=None, help='specific file to process')
        parser.add_argument('--dir', 
                            nargs=1, default=None, help='specific dir to process')
        parser.add_argument('-v', '--verbose', 
                            action='store_true', help='verbose mode')
        parser.add_argument('--ignore-file-list', 
                            dest='ignore_file_list', metavar='filename', nargs='+', default=tuple(), help='ignore file name list')
        args = parser.parse_args()
        self.parser = parser
        self.args = args
        
        if args.cmd not in ['compile_pye', 'compile_all_pye']:
            raise PyConcreteError("arg: compile_pye, need provide the file [--file] to process")
        args.compile_pye = bool(args.cmd == 'compile_pye')
        args.compile_all_pye = bool(args.cmd == 'compile_all_pye')
        if args.compile_pye:
            if args.file is None:
                raise PyConcreteError("arg: compile_pye, need provide the file [--file] to process")
            args.compile_pye = args.file[0]
        elif args.compile_all_pye:
            if args.dir is None:
                raise PyConcreteError("arg: compile_all_pye, need provide the dir [--dir] to process")
            args.compile_all_pye = args.dir[0]
        
        if args.verbose:
            print 'compile_pye=%s' % args.compile_pye
            print 'compile_all_pye=%s' % args.compile_all_pye
            print 'ignore_file_list=%s' % str(args.ignore_file_list)
            print 'verbose=%s' % args.verbose
        
    def run(self):
        if self.args.compile_pye:
            filepath = self.args.compile_pye
            if not isfile(filepath):
                raise PyConcreteError("arg: compile_pye, the file doesn't exists (%s)" % filepath)
            self.compile_pye_file(filepath)
        elif self.args.compile_all_pye:
            dirpath = self.args.compile_all_pye
            if not isdir(dirpath):
                raise PyConcreteError("arg: compile_all_pye, the dir doesn't exists (%s)" % dirpath)
            self.compile_pye_dir(dirpath)
        else:
            print 'please input correct command!'
            self.parser.print_help()
            
    def compile_pye_dir(self, folder):
        print 'handle dir=%s' % folder
        for f in os.listdir(folder):
            if f in ['.', '..', '.git', '.svn', 'pyconcrete']:
                continue
            fullpath = join(folder, f)
            if isdir(fullpath) and self.args.recursive:
                self.compile_pye_dir(fullpath)
            elif fullpath.endswith('.py'):
                self.compile_pye_file(fullpath)
                
    def compile_pye_file(self, py_file):
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
