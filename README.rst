A simple HTTP proxy for Elastic Search
######################################

A web application that proxies the HTTP requests to Elastic Search.
The most used queries will be automatically cached into memory (this uses
memcache for now), avoiding to query Elastic Search each time.

To start the application on port 9201, type::

  python webproxy.py --local localhost:9201 --distant localhost:9200
