import argparse
import sys

from chaussette.server import make_server
from chaussette.backend import backends

from wsgiproxy.app import WSGIProxyApp

from httpcache.webproxy import CacheRequests
from httpcache.utils import configure_logger, LOG_LEVELS
from httpcache import logger


def get_args():
    parser = argparse.ArgumentParser(description='An HTTP proxy, with cache.')

    parser.add_argument('--local', default='localhost:8080',
                        help='host/port of the local proxy')
    parser.add_argument('--distant', default='localhost:8000',
                        help='host/port of the distant server')

    parser.add_argument('--cache', default=None,
                        help='host:port of the memcache server, if any')

    parser.add_argument('--cache-timeout', default=5 * 60, type=int,
                        help='Cache timeout, in seconds')

    parser.add_argument('--statsd', default=None,
                        help='host:port of the statsd server, if any')
    parser.add_argument('--statsd-namespace', default='httpcache',
                        help='namespace to use when sending statsd messages')

    parser.add_argument('--excluded-paths', default=None,
                        help='a comma-separated list of paths to exclude')

    parser.add_argument('--backend', type=str, default='fastgevent',
                        choices=backends(),
                        help='The http backend to use to serve the requests.')

    log_levels = LOG_LEVELS.keys() + [key.upper() for key in LOG_LEVELS.keys()]
    parser.add_argument('--log-level', dest='loglevel', default='info',
                        choices=log_levels, help="log level")

    parser.add_argument('--log-output', dest='logoutput', default='-',
                        help="log output")
    return parser.parse_args()


def main():
    args = get_args()

    configure_logger(logger, args.loglevel, args.logoutput)

    cache = None
    if args.cache:
        import pylibmc
        logger.info('Using the cache at %s' % args.cache)
        logger.info('The timeout value is set to %ss' % args.cache_timeout)
        cache = pylibmc.Client([args.cache])

    statsd = None
    if args.statsd:
        import statsd
        logger.info('sending informations to statsd at %s' % args.statsd)
        statsd_host, statsd_port = args.statsd.split(':', 1)
        statsd = statsd.StatsClient(statsd_host, int(statsd_port),
                                    args.statsd_namespace)

    if args.excluded_paths and not cache:
        logger.info('--excluded-paths ignored; since no cache is being used')

    elif args.excluded_paths:
        args.excluded_paths = args.excluded_paths.split(',')
        logger.info('paths that will not be cached:' % args.excluded_paths)

    host, port = args.local.split(':')
    port = int(port)

    if not args.distant.startswith('http://'):
        args.distant = 'http://%s' % args.distant

    logger.info('Starting httpcache proxy. Listening on %s, proxying to %s, '
                'using the %s backend'
                % (args.local, args.distant, args.backend))

    proxy = WSGIProxyApp(args.distant)
    app = CacheRequests(proxy, cache=cache, statsd=statsd,
                        cache_timeout=args.cache_timeout,
                        excluded_paths=args.excluded_paths, logger=logger)

    httpd = make_server(app, host, port=port, backend=args.backend)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        logger.info('Exiting, bye!')


if __name__ == '__main__':
    main()
