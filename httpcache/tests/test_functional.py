import sys
import subprocess
import time
from unittest import TestCase

import requests

_CMD = [sys.executable, '-m', 'httpcache.run', '--cache',
        '--local', '8000',
        '--distant', 'localhost:8888']

_PROXY = 'http://localhost:8000'
_SERVER = [sys.executable, '-m', 'httpcache.tests.httpserver', '8888']


class TestProxy(TestCase):
    def setUp(self):
        self._run = subprocess.Popen(_CMD)
        time.sleep(.5)
        if self._run.poll():
            raise ValueError("Could not start the proxy")

        self._web = subprocess.Popen(_SERVER)
        time.sleep(.5)
        if self._web.poll():
            raise ValueError("Could not start the wev server")

    def tearDown(self):
        self._run.terminate()
        self._web.terminate()

    def test_proxy(self):
        # let's do a simple request first to make sure the proxy works
        res = requests.get(_PROXY)
        self.assertEquals(res.status_code, 200)

        # the call count should be 1.
        from pdb import set_trace; set_trace()
        request.get(_PROXY + '/count')
