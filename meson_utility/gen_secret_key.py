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
import hashlib
import sys

PY2 = sys.version_info.major < 3
SECRET_HEADER_PATH = 'secret_key.h'


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
    """ % (
        factor,
        len(key),
        key_val_code,
    )

    with open(SECRET_HEADER_PATH, 'w') as f:
        f.write(code)


if __name__ == '__main__':
    passphrase = sys.argv[1]
    k, f = hash_key(passphrase.encode('utf8'))
    create_secret_key_header(k, f)
