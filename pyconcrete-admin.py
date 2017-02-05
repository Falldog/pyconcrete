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
import unittest
import argparse
import py_compile
import subprocess
from os.path import abspath, dirname, join, exists, isdir, isfile

CUR_DIR = dirname(abspath(__file__))
VALID_CMD = ['compile', 'test', 'release']


class PyConcreteError(Exception):
    pass


class PyConcreteAdmin(object):
    def __init__(self):
        self.parser = None
        self.args = None
        self.parse_arg()

    def parse_arg(self):
        """
        Example:
            compile file/dir to .pye
            pyconcrete-admin.py compile --source={file} --pye

            compile file/dir to .pyc
            pyconcrete-admin.py compile --source={file} --pyc
        """
        parser = argparse.ArgumentParser(description='PyConcreteAdmin')
        parser.add_argument('cmd',
                            default='', help=' | '.join(VALID_CMD))
        parser.add_argument('--pye',
                            dest='pye', action='store_true', help='process on .pye')
        parser.add_argument('--pyc',
                            dest='pyc', action='store_true', help='process on .pyc')
        parser.add_argument('-s', '--source',
                            dest='source', default=None, help='specific the source to process, source could be file/dir')
        parser.add_argument('--remove-py',
                            dest='remove_py', action='store_true', help='remove .py after compile pye')
        parser.add_argument('--remove-pyc',
                            dest='remove_pyc', action='store_true', help='remove .pyc after compile pye')
        parser.add_argument('-v', '--verbose',
                            action='store_true', help='verbose mode')
        parser.add_argument('--test-module',
                            dest='test_module', default=None, help='test on single module')
        parser.add_argument('--ignore-file-list',
                            dest='ignore_file_list', metavar='filename', nargs='+', default=tuple(), help='ignore file name list')
        args = parser.parse_args()
        self.parser = parser
        self.args = args

        if args.cmd not in VALID_CMD:
            raise PyConcreteError("please provide correct command")

        args.compile = bool(args.cmd == 'compile')
        args.test = bool(args.cmd == 'test')
        args.release = bool(args.cmd == 'release')
        if args.compile:
            if args.source is None:
                raise PyConcreteError("arg: compile, need assign --source={file/dir} to process")
            if not args.pye and not args.pyc:
                raise PyConcreteError("arg: compile, need assign the type for compile to `pye` or `pyc`")

        if args.verbose:
            print('compile on "%s"' % args.source)
            print('ignore-file-list=%s' % str(args.ignore_file_list))
            print('verbose=%s' % args.verbose)

    def run(self):
        args = self.args
        if args.compile:
            self.compile()
        elif args.test:
            self.test()
        elif args.release:
            self.release()
        else:
            print('please input correct command!')
            self.parser.print_help()

    def compile(self):
        args = self.args
        if isfile(args.source):
            if not args.source.endswith('.py'):
                raise PyConcreteError("source file should end with .py")

            if args.pye:
                self.compile_pye_file(args.source)
            elif args.pyc:
                self.compile_pyc_file(args.source)

        elif isdir(args.source):
            self.compile_dir(args.source)

    def compile_dir(self, folder):
        for f in os.listdir(folder):
            if f in ['.', '..', '.git', '.svn', 'pyconcrete'] or f in self.args.ignore_file_list:
                continue
            fullpath = join(folder, f)
            if isdir(fullpath):
                self.compile_dir(fullpath)
            elif fullpath.endswith('.py'):
                if self.args.pye:
                    self.compile_pye_file(fullpath)
                elif self.args.pyc:
                    self.compile_pyc_file(fullpath)

    def compile_pyc_file(self, py_file):
        pyc_file = py_file + 'c'
        pyc_exists = exists(pyc_file)
        if not pyc_exists or os.stat(py_file).st_mtime != os.stat(pyc_file).st_mtime:
            py_compile.compile(py_file, cfile=pyc_file)
            if self.args.verbose:
                print('* create %s' % pyc_file)
        else:
            if self.args.verbose:
                print('* skip %s' % pyc_file)

        if self.args.remove_py:
            os.remove(py_file)

    def compile_pye_file(self, py_file):
        """
        if there is no .pyc file, compile .pyc first
        then compile .pye
        """
        import pyconcrete
        pyc_file = py_file + 'c'
        pye_file = py_file + 'e'
        pyc_exists = exists(pyc_file)
        if not pyc_exists or os.stat(py_file).st_mtime != os.stat(pyc_file).st_mtime:
            py_compile.compile(py_file, cfile=pyc_file)
        if not exists(pye_file) or os.stat(py_file).st_mtime != os.stat(pye_file).st_mtime:
            pyconcrete.encrypt_file(pyc_file, pye_file)
            if self.args.verbose:
                print('* create %s' % pye_file)
        else:
            if self.args.verbose:
                print('* skip %s' % pye_file)

        # .pyc doesn't exists at beginning, remove it after .pye created
        if not pyc_exists or self.args.remove_pyc:
            os.remove(pyc_file)
        if self.args.remove_py:
            os.remove(py_file)

    def test(self):
        test_dir = join(CUR_DIR, 'test')
        sys.path.insert(0, test_dir)  # for loadTestsFromName

        if self.args.test_module:
            suite = unittest.TestLoader().loadTestsFromName(self.args.test_module)
        else:
            suite = unittest.TestLoader().discover(test_dir)

        verbosity = 2 if self.args.verbose else 1
        unittest.TextTestRunner(verbosity=verbosity).run(suite)

    def release(self):
        try:
            import pypandoc
            readme = pypandoc.convert('README.md', 'rst')
            with open('README.rst', 'wb') as f:
                f.write(readme)
        except ImportError:
            print('you need to install pypandoc before release pyconcrete')

        subprocess.call('python setup.py sdist', shell=True)  # ignore can't found README error
        subprocess.check_output('twine upload dist/*', shell=True)
        subprocess.check_output('rm README.rst', shell=True)
        subprocess.check_output('rm -rf build', shell=True)
        subprocess.check_output('rm -rf dist', shell=True)

if __name__ == '__main__':
    admin = PyConcreteAdmin()
    admin.run()
