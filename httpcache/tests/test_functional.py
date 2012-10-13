import sys
import subprocess
import time
from unittest import TestCase

import requests

_CMD = [sys.executable, '-m', 'httpcache.run',
        '--backend', 'wsgiref',
        '--cache', 'localhost:11211',
        '--cache-timeout', '1',
        '--local', 'localhost:8000',
        '--distant', 'localhost:8080']

_PROXY = 'http://localhost:8000'
_PROXIED = 'http://localhost:8080'
_SERVER = [sys.executable, '-m', 'httpcache.tests.httpserver', '8080']


class TestProxy(TestCase):
    def setUp(self):
        self._run = subprocess.Popen(_CMD)
        time.sleep(.5)
        if self._run.poll():
            raise ValueError("Could not start the proxy")

        self._web = subprocess.Popen(_SERVER)
        time.sleep(.5)
        if self._web.poll():
            self._run.terminate()
            raise ValueError("Could not start the web server")

    def tearDown(self):
        self._run.terminate()
        self._web.terminate()

    def test_proxy(self):
        # let's do a simple request first to make sure the proxy works
        res = requests.get(_PROXY)
        self.assertEquals(res.status_code, 200)

        self.assertEquals(requests.get(_PROXIED + '/count').text, '1')

        res = requests.get(_PROXY)
        res = requests.get(_PROXY)
        self.assertEquals(requests.get(_PROXIED + '/count').text, '1')

        # wait a bit so that we invalidate the cache (set to 1s)
        time.sleep(1)
        res = requests.get(_PROXY)

        # another call should have been made.
        self.assertEquals(requests.get(_PROXIED + '/count').text, '2')
