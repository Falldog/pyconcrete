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

import logging
import os
import sys
import time
import unittest
from multiprocessing import Process, Queue
from os.path import abspath, dirname, join
from test import base
from zipfile import ZipFile

CUR_DIR = abspath(dirname(__file__))
ROOT_DIR = abspath(join(CUR_DIR, '..'))
DATA_DIR = join(CUR_DIR, 'data')
REQUEST_ZIP = join(DATA_DIR, 'requests-2.27.1.zip')  # zip structure: first level must contain `requests` folder
REQUEST_MAIN = join(DATA_DIR, 'main_requests.py')
PYADMIN_PATH = join(ROOT_DIR, 'pyconcrete-admin.py')
RUN_COUNT = int(os.environ.get('TEST_PYE_PERFORMANCE_COUNT', '5'))

logger = logging.getLogger('pyconcrete')


def main_requests(import_concrete, q):
    """
    testing main function for multiprocessing
    purpose: testing import without exception
    """
    if import_concrete:
        import pyconcrete  # noqa: F401

    t = time.time()
    import requests  # noqa: F401
    from requests.adapters import HTTPAdapter  # noqa: F401
    from requests.auth import HTTPDigestAuth, _basic_auth_str  # noqa: F401
    from requests.compat import Morsel, builtin_str, cookielib, getproxies, is_py3, str, urljoin, urlparse  # noqa: F401
    from requests.cookies import cookiejar_from_dict, morsel_to_cookie  # noqa: F401
    from requests.exceptions import ConnectionError  # noqa: F401
    from requests.exceptions import ConnectTimeout  # noqa: F401
    from requests.exceptions import InvalidSchema  # noqa: F401
    from requests.exceptions import InvalidURL  # noqa: F401
    from requests.exceptions import MissingSchema  # noqa: F401
    from requests.exceptions import ReadTimeout  # noqa: F401
    from requests.exceptions import RetryError  # noqa: F401
    from requests.exceptions import Timeout  # noqa: F401
    from requests.hooks import default_hooks  # noqa: F401
    from requests.models import PreparedRequest, urlencode  # noqa: F401
    from requests.sessions import SessionRedirectMixin  # noqa: F401
    from requests.structures import CaseInsensitiveDict  # noqa: F401

    t = time.time() - t
    q.put(requests.__file__)
    q.put(t)


@unittest.skipIf(not os.path.exists(REQUEST_ZIP), "requests zip file doesn't exists")
class TestPerformance(base.TestPyConcreteBase):
    def setUp(self):
        super(TestPerformance, self).setUp()

        zip = ZipFile(REQUEST_ZIP)
        zip.extractall(self.tmp_dir)
        zip.close()

        self.req_dir = join(self.tmp_dir, 'requests')
        base.touch(join(self.req_dir, '__init__.py'))

    def _test_requests(self, import_concrete):
        sys.path.insert(0, self.req_dir)

        q = Queue()
        p = Process(target=main_requests, args=(import_concrete, q))

        p.start()
        path = q.get(timeout=5)
        t = q.get(timeout=2)
        p.join()

        self.assertTrue(path.startswith(self.req_dir), "wrong import path of requests = %s" % path)
        return t

    def test_requests_pye(self):
        self.lib_compile_pye(self.req_dir, remove_py=True, remove_pyc=True)
        t = 0.0
        for i in range(RUN_COUNT):
            t += self._test_requests(True)
        logger.info(
            'test import request (pye) [count=%d] total time = %.2f, avg time = %.2f' % (RUN_COUNT, t, t / RUN_COUNT)
        )

    def test_requests_pyc(self):
        self.lib_compile_pyc(self.req_dir, remove_py=True)
        t = 0.0
        for i in range(RUN_COUNT):
            t += self._test_requests(False)
        logger.info(
            'test import request (pyc) [count=%d] total time = %.2f, avg time = %.2f' % (RUN_COUNT, t, t / RUN_COUNT)
        )

    def test_requests_pyc_with_import_hooker(self):
        self.lib_compile_pyc(self.req_dir, remove_py=True)
        t = 0.0
        for i in range(RUN_COUNT):
            t += self._test_requests(True)
        logger.info(
            'test import request (pyc) (import hooker) [count=%d] total time = %.2f, avg time = %.2f'
            % (RUN_COUNT, t, t / RUN_COUNT)
        )

    def test_requests_py(self):
        t = 0.0
        for i in range(RUN_COUNT):
            t += self._test_requests(False)
        logger.info(
            'test import request (py) [count=%d] total time = %.2f, avg time = %.2f' % (RUN_COUNT, t, t / RUN_COUNT)
        )

    def test_requests_py_with_import_hooker(self):
        t = 0.0
        for i in range(RUN_COUNT):
            t += self._test_requests(True)
        logger.info(
            'test import request (py) (import hooker) [count=%d] total time = %.2f, avg time = %.2f'
            % (RUN_COUNT, t, t / RUN_COUNT)
        )


if __name__ == '__main__':
    unittest.main()
