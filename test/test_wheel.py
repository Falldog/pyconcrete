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
import subprocess
from test import base

from src.config import PASSPHRASE_ENV


class TestWheel(base.TestPyConcreteBase):
    def test_building_by_wheel(self):
        env = os.environ.copy()
        env[PASSPHRASE_ENV] = 'test'
        sp = subprocess.run('pip wheel .', env=env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if sp.returncode != 0:
            print(sp.stdout.decode('utf-8'))
            raise Exception("pip create wheel fail...")
