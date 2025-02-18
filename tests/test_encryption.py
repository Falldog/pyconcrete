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
from os.path import join
from subprocess import PIPE, Popen

import pytest


def _encrypt_plain_buffer_and_decrypt(venv, tmpdir, plain_buffer):
    """
    pye_cli will always transform .py to .pyc and then encrypt it as .pye
    here want to test AES encryption, We should not convert it to .pyc. or it will chnage the text length to encryption.
    We try to encrypt by custom script to keep the text as original.
    """
    executor_py = join(tmpdir, 'executor.py')
    plain_file = join(tmpdir, 'plain_buffer.text')
    encrypted_file = join(tmpdir, 'encrypted.text')

    # create executor py file
    with open(executor_py, "w") as f:
        executor_py_source = """
import sys
import pyconcrete
plain_buffer = sys.argv[1]
encrypted = sys.argv[2]
pyconcrete.encrypt_file(plain_buffer, encrypted)
with open(encrypted, 'rb') as f:
    data = f.read()
print(pyconcrete.decrypt_buffer(data).decode('utf-8'))
            """.strip()
        f.write(executor_py_source)

    # create plain file
    with open(plain_file, 'w') as f:
        f.write(plain_buffer)

    # run executor py file to encrypt as file and decrypt via buffer
    cmds = [venv.executable, executor_py, plain_file, encrypted_file]
    p = Popen(cmds, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
    stdout, stderr = p.communicate(input=plain_buffer)
    return stdout


@pytest.mark.parametrize(
    "plain_buffer",
    [
        # less than 1 AES block (16)
        "1",
        "12",
        "123",
        "12345",
        "12345678",
        # 1 AES block (16)
        "1234567890ABCDEF",
        # more than 1 AES block (16)
        "1234567890ABCDEF,\n" * 10,
    ],
)
def test_encryption__aes_block_testing(venv, pye_cli, tmpdir, plain_buffer):
    # execution
    output = _encrypt_plain_buffer_and_decrypt(venv, tmpdir, plain_buffer)

    # verification
    assert output == (plain_buffer + '\n')  # without output.strip() to make sure the output is exactly what we want
