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
import string
import hashlib
from os.path import join
from distutils.core import setup, Extension
from distutils.command.build import build

DEFAULT_KEY = 'Falldog'

CUR_DIR = os.path.dirname(__file__)
SRC_DIR = join('src', 'pyconcrete_ext')
SECRET_HEADER_PATH = join(SRC_DIR, 'secret_key.h')

def hash_key(key):
    factor = sum([ord(s) for s in key])
    factor %= 128
    if factor < 16:
        factor += 16
    
    m = hashlib.md5()
    m.update(key)
    k = m.digest()
    
    return k, factor
    
def gen_secret_key_header(key, factor):
    # reference from http://stackoverflow.com/questions/1356896/how-to-hide-a-string-in-binary-code
    # encrypt the secret key in binary code
    # avoid to easy read from HEX view
    
    key_val_lst = []
    for i, k in enumerate(key):
        key_val_lst.append("(0x%X ^ (0x%X - %d))" % (ord(k), factor, i))
    key_val_code = string.join(key_val_lst, ', ')
    
    code = """
        #define SECRET_NUM 0x%X
        static const unsigned char* GetSecretKey()
        {
            unsigned int i = 0;
            static unsigned char key[] = {%s, 0/* terminal char */};
            static int is_encrypt = 1/*true*/;
            if( is_encrypt )
            {
                for(i = 0 ; i < sizeof(key) / sizeof(key[0]) - 1 ; ++i)
                {
                    key[i] = key[i] ^ (SECRET_NUM - i);
                }
                is_encrypt = 0/*false*/;
            }
            return key;
        }
    """ % (factor, key_val_code)
    
    with open(SECRET_HEADER_PATH, 'w') as f:
        f.write(code)
    
def remove_secret_key_header():
    os.remove(SECRET_HEADER_PATH)

    
    
class build_ex(build):
    '''
    execute extra function before/after build.run()
    '''
    user_options = build.user_options + [
      ('passphrase=', None, 'specify passphrase'),
    ]
    
    def initialize_options(self):
        build.initialize_options(self)
        self.passphrase = None

    def pre_build(self):
        if not self.passphrase:
            self.passphrase = raw_input("please input the passphrase \nfor encrypt your python script (enter for default) : \n")
            if len(passphrase) == 0:
                self.passphrase = DEFAULT_KEY
            else:
                passphrase2 = raw_input("please input again to confirm\n")
                if self.passphrase != passphrase2:
                    raise Exception("Passphrase is different")
        k, f = hash_key(self.passphrase)
        gen_secret_key_header(k, f)
        
    def post_build(self):
        remove_secret_key_header()
        
    def run(self):
        self.pre_build()
        ret = build.run(self)
        self.post_build()
        return ret

        
include_dirs = [join(SRC_DIR, 'openaes', 'inc')]
if sys.platform == 'win32':
    include_dirs.append(join(SRC_DIR, 'include_win'))
    
module = Extension('_pyconcrete',
                    include_dirs = include_dirs, 
                    sources = [join(SRC_DIR, 'pyconcrete.c'),
                               join(SRC_DIR, 'openaes', 'src', 'oaes.c'),
                               join(SRC_DIR, 'openaes', 'src', 'oaes_base64.c'),
                               join(SRC_DIR, 'openaes', 'src', 'oaes_lib.c')])

setup( name = 'PyConcrete',
       version = '1.0',
       description = 'protect your python script',
       ext_modules = [module],
       cmdclass={"build": build_ex} )
