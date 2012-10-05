#!/usr/bin/env python
import sys
import urllib2
from urlparse import urlparse, urljoin


class Application(object):

    def __init__(self, distant, cache=None):
        self.distant = distant
        self.cache = cache

    def __call__(self, env, start_response):
        method = env['REQUEST_METHOD']
        path = env['PATH_INFO']

        if env['QUERY_STRING']:
            path += '?' + env['QUERY_STRING']

        return self.proxy(method, path, start_response)

    def proxy(self, method, path, start_response):
        path = urljoin(self.distant, path)
        try:
            try:
                response = urllib2.urlopen(path)
            except urllib2.HTTPError:
                response = sys.exc_info()[1]
            scheme, netloc, path, params, query, fragment = urlparse(path)
        except Exception:
            sys.stderr.write('error while reading %s:\n' % path)
            start_response('502 Bad Gateway', [('Content-Type', 'text/html')])
            return
        else:
            start_response('%s %s' % (response.code, response.msg),
                           response.headers.items())
            data = response.read()
            return [data]
