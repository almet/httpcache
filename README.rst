A simple HTTP proxy to handle cache
###################################

A web application that proxies HTTP requests to another HTTP server, caching
the results if asked to.

To start the cache on port 9201 with a cache expiring every 2 seconds, type::

  $ httpcache --local localhost:9201 --distant localhost:9200 --cache localhost:11211 --cache-timeout 2

Specify the backend
===================

You can also use a different backend if that makes sense for you. You can use
one of the backends exposed by `chaussette <http://chaussette.rtfd.org>`_

Using statsd
============

You can send information to a statsd server each time a request is proxied, if
it hits the proxied server or if it hits the cache.

