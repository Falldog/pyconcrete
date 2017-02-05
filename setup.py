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
import hashlib
from os.path import join
from distutils.core import setup, Extension, Command
from distutils.command.build import build
from distutils.command.install import install
from src.config import DEFAULT_KEY, TEST_DIR, SRC_DIR, PY_SRC_DIR, EXT_SRC_DIR, SECRET_HEADER_PATH

PY2 = sys.version_info[0] < 3


# .rst should created by pyconcrete-admin
if os.path.exists('README.rst'):
    readme_path = 'README.rst'
else:
    readme_path = 'README.md'
with open(readme_path, 'r') as f:
    readme = f.read()

try:
   input = raw_input
except NameError:
   pass


def hash_key(key):
    if PY2:
        factor = sum([ord(s) for s in key])
    else:
        factor = sum([s for s in key])
    factor %= 128
    if factor < 16:
        factor += 16
    
    m = hashlib.md5()
    m.update(key)
    k = m.digest()
    
    return k, factor


def create_secret_key_header(key, factor):
    # reference from - http://stackoverflow.com/questions/1356896/how-to-hide-a-string-in-binary-code
    # encrypt the secret key in binary code
    # avoid to easy read from HEX view
    
    key_val_lst = []
    for i, k in enumerate(key):
        n = ord(k) if PY2 else k
        key_val_lst.append("(0x%X ^ (0x%X - %d))" % (n, factor, i))
    key_val_code = ", ".join(key_val_lst)
    
    code = """
        #define SECRET_NUM 0x%X
        #define SECRET_KEY_LEN %d
        static const unsigned char* GetSecretKey()
        {
            unsigned int i = 0;
            static unsigned char key[] = {%s, 0/* terminal char */};
            static int is_encrypt = 1/*true*/;
            if( is_encrypt )
            {
                for(i = 0 ; i < SECRET_KEY_LEN ; ++i)
                {
                    key[i] = key[i] ^ (SECRET_NUM - i);
                }
                is_encrypt = 0/*false*/;
            }
            return key;
        }
    """ % (factor, len(key), key_val_code)
    
    with open(SECRET_HEADER_PATH, 'w') as f:
        f.write(code)


def remove_secret_key_header():
    if os.path.exists(SECRET_HEADER_PATH):
        os.remove(SECRET_HEADER_PATH)


class CmdBase:
    def pre_process(self):
        self.manual_create_secrete_key_file = not os.path.exists(SECRET_HEADER_PATH)
        if self.manual_create_secrete_key_file:
            if not self.passphrase:
                self.passphrase = input("please input the passphrase \nfor encrypt your python script (enter for default) : \n")
                if len(self.passphrase) == 0:
                    self.passphrase = DEFAULT_KEY
                else:
                    passphrase2 = input("please input again to confirm\n")
                    if self.passphrase != passphrase2:
                        raise Exception("Passphrase is different")
        
            k, f = hash_key(self.passphrase.encode('utf8'))
            create_secret_key_header(k, f)
        
    def post_process(self):
        if self.manual_create_secrete_key_file:
            remove_secret_key_header()


class BuildEx(CmdBase, build):
    """
    execute extra function before/after build.run()
    """
    user_options = build.user_options + [('passphrase=', None, 'specify passphrase')]
    
    def initialize_options(self):
        build.initialize_options(self)
        self.passphrase = None

    def run(self):
        self.pre_process()
        ret = build.run(self)
        self.post_process()
        return ret


class InstallEx(CmdBase, install):
    """
    execute extra function before/after install.run()
    """
    user_options = install.user_options + [('passphrase=', None, 'specify passphrase')]
    
    def initialize_options(self):
        install.initialize_options(self)
        self.passphrase = None

    def run(self):
        self.pre_process()
        ret = install.run(self)
        self.post_process()
        self.create_pth()
        return ret

    def create_pth(self):
        """
        create pyconcrete.pth for automatic import pyconcrete after python launched
        """
        # setup(
        #     data_files=(sysconfig.get_python_lib(), 'pyconcrete.pth'),
        #     ...
        # )
        # it will got wrong result in ubuntu, get_python_lib got /usr/lib
        # but pyconcrete installed in /usr/local/lib
        #
        # get install_libbase to avoid this issue
        filename = join(self.install_libbase, 'pyconcrete.pth')
        with open(filename, 'w') as f:
            f.write('import pyconcrete')
        print('creating %s' % filename)


class TestEx(Command):
    description = "Running all unit test for pyconcrete"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import unittest
        suite = unittest.TestLoader().discover(TEST_DIR)
        unittest.TextTestRunner(verbosity=2).run(suite)


version = imp.load_source('version', join(PY_SRC_DIR, 'version.py'))

include_dirs = [join(EXT_SRC_DIR, 'openaes', 'inc')]
if sys.platform == 'win32':
    include_dirs.append(join(EXT_SRC_DIR, 'include_win'))
    
module = Extension(
    'pyconcrete._pyconcrete',
    include_dirs=include_dirs,
    sources=[
        join(EXT_SRC_DIR, 'pyconcrete.c'),
        join(EXT_SRC_DIR, 'openaes', 'src', 'oaes.c'),
        join(EXT_SRC_DIR, 'openaes', 'src', 'oaes_base64.c'),
        join(EXT_SRC_DIR, 'openaes', 'src', 'oaes_lib.c'),
    ],
)

setup(
    name='pyconcrete',
    version=version.__version__,
    description='Protect your python script, encrypt it as .pye and decrypt when import it',
    long_description=readme,
    keywords='python source encryption obfuscation',
    author='Falldog',
    author_email='falldog7@gmail.com',
    url='https://github.com/Falldog/pyconcrete',
    license="Apache License 2.0",
    ext_modules=[module],
    cmdclass={
        "build": BuildEx,
        "install": InstallEx,
        "test": TestEx,
    },
    scripts=[
        'pyconcrete-admin.py',
    ],
    packages=[
        'pyconcrete',
    ],
    package_dir={
        '': SRC_DIR,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: Apache Software License',
    ],
)
