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
        subparsers = parser.add_subparsers()

        # === compile === #
        parser_compile = subparsers.add_parser('compile', help='compile .pye')
        parser_compile.add_argument('-s', '--source', dest='source', default=None,
                                    help='specific the source to process, source could be file/dir')
        parser_compile.add_argument('--pye', dest='pye', action='store_true', help='process on .pye')
        parser_compile.add_argument('--pyc', dest='pyc', action='store_true', help='process on .pyc')
        parser_compile.add_argument('--remove-py', dest='remove_py', action='store_true',
                                    help='remove .py after compile pye')
        parser_compile.add_argument('--remove-pyc', dest='remove_pyc', action='store_true',
                                    help='remove .pyc after compile pye')
        parser_compile.add_argument('-i', '--ignore-file-list', dest='ignore_file_list', metavar='filename', nargs='+',
                                    default=tuple(), help='ignore file name list')
        parser_compile.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
        parser_compile.set_defaults(func=self.compile)

        # === test === #
        parser_test = subparsers.add_parser('test', help='test pycocnrete')
        parser_test.add_argument('-m', '--module', dest='test_module', default=None, help='test on single module')
        parser_test.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
        parser_test.set_defaults(func=self.test)

        # === release === #
        parser_release = subparsers.add_parser('release', help='release pyconcrete for github')
        parser_release.set_defaults(func=self.release)

        args = parser.parse_args()
        args.func(args)

    def compile(self, args):
        if args.source is None:
            raise PyConcreteError("arg: compile, need assign --source={file/dir} to process")
        if not args.pye and not args.pyc:
            raise PyConcreteError("arg: compile, need assign the type for compile to `pye` or `pyc`")

        if isfile(args.source):
            if not args.source.endswith('.py'):
                raise PyConcreteError("source file should end with .py")

            if args.pye:
                self._compile_pye_file(args, args.source)
            elif args.pyc:
                self._compile_pyc_file(args, args.source)

        elif isdir(args.source):
            self._compile_dir(args, args.source)

    def _compile_dir(self, args, folder):
        for f in os.listdir(folder):
            if f in ['.', '..', '.git', '.svn', 'pyconcrete'] or f in args.ignore_file_list:
                continue
            fullpath = join(folder, f)
            if isdir(fullpath):
                self._compile_dir(args, fullpath)
            elif fullpath.endswith('.py'):
                if args.pye:
                    self._compile_pye_file(args, fullpath)
                elif args.pyc:
                    self._compile_pyc_file(args, fullpath)

    def _compile_pyc_file(self, args, py_file):
        pyc_file = py_file + 'c'
        pyc_exists = exists(pyc_file)
        if not pyc_exists or os.stat(py_file).st_mtime != os.stat(pyc_file).st_mtime:
            py_compile.compile(py_file, cfile=pyc_file)
            if args.verbose:
                print('* create %s' % pyc_file)
        else:
            if args.verbose:
                print('* skip %s' % pyc_file)

        if args.remove_py:
            os.remove(py_file)

    def _compile_pye_file(self, args, py_file):
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
            if args.verbose:
                print('* create %s' % pye_file)
        else:
            if args.verbose:
                print('* skip %s' % pye_file)

        # .pyc doesn't exists at beginning, remove it after .pye created
        if not pyc_exists or args.remove_pyc:
            os.remove(pyc_file)
        if args.remove_py:
            os.remove(py_file)

    def test(self, args):
        test_dir = join(CUR_DIR, 'test')
        sys.path.insert(0, test_dir)  # for loadTestsFromName

        if args.test_module:
            suite = unittest.TestLoader().loadTestsFromName(args.test_module)
        else:
            suite = unittest.TestLoader().discover(test_dir)

        verbosity = 2 if args.verbose else 1
        result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
        if not result.wasSuccessful():
            sys.exit(1)

    def release(self, args):
        try:
            import pypandoc
            readme = pypandoc.convert('README.md', 'rst')
            with open('README.rst', 'wb') as f:
                f.write(readme)
        except ImportError:
            print('you need to install `pypandoc` before release pyconcrete')

        subprocess.call('python setup.py sdist', shell=True)  # ignore can't found README error
        subprocess.check_output('twine upload dist/*', shell=True)
        subprocess.check_output('rm README.rst', shell=True)
        subprocess.check_output('rm -rf build', shell=True)
        subprocess.check_output('rm -rf dist', shell=True)


if __name__ == '__main__':
    admin = PyConcreteAdmin()
    # admin.run()
