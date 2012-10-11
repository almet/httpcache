#!/usr/bin/env python
import hashlib

from webob.dec import wsgify


class CacheRequests(object):

    def __init__(self, app, cache=None, cache_timeout=5 * 60,
                 statsd=None, excluded_paths=None, logger=None):
        self._cache = cache
        self._cache_timeout = cache_timeout
        self._app = app
        self._excluded_paths = excluded_paths or ()
        self._logger = logger
        self._statsd = statsd

    @wsgify
    def __call__(self, req):
        return self._get_from_server_or_cache(req)

    def _get_from_server_or_cache(self, req):
        if (req.method == 'GET' and self._cache and
            # we don't want to check the cache if the path is to be ignored
            not any([req.path in exc for exc in self._excluded_paths])):

            digest = hashlib.sha224(req.path_qs).hexdigest()
            key = '%s-%s' % (self._app.href, digest)
            result = self._cache.get(key)
            if result is None:
                result = self._raw_call(req)
                self._cache.set(key, result, self._cache_timeout)
            else:
                if self._statsd:
                    self._statsd.incr('cache-' + req.path_qs)
                self._logger.debug('Hitting the cache for %s' % req.path_qs)
        else:
            if self._statsd:
                self._statsd.incr('call-' + req.path_qs)
            result = self._raw_call(req)
        return result

    def _raw_call(self, req):
        self._logger.debug('Hitting the proxied server for %s' % req.path_qs)
        self._statsd.incr('call-' + req.path_qs)
        return req.get_response(self._app)
