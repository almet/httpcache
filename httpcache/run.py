import argparse
import sys

from paste import httpserver
from wsgiproxy.app import WSGIProxyApp

from httpcache.webproxy import CacheRequests
from httpcache.utils import configure_logger, LOG_LEVELS
from httpcache import logger


def get_args():
    parser = argparse.ArgumentParser(description='An HTTP proxy, with cache.')

    parser.add_argument('--local', default='localhost:9201',
                        help='host/port of the local proxy')
    parser.add_argument('--distant', default='localhost:9200',
                        help='host/port of the distant server')

    parser.add_argument('--cache', default=None,
                        help='host:port of the memcache server, if any')

    parser.add_argument('--cache-timeout', default=5 * 60, type=int,
                        help='Cache timeout, in seconds')

    parser.add_argument('--statsd', default=None,
                        help='host:port of the statsd server, if any')

    parser.add_argument('--excluded-paths', default=None,
                        help='a comma-separated list of paths to exclude')

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
        statsd = statsd.StatsClient(args.statsd.split(':', 1))

    if args.excluded_paths and not cache:
        logger.info('--excluded-paths ignored; since no cache is being used')

    elif args.excluded_paths:
        args.excluded_paths = args.excluded_paths.split(',')
        logger.info('paths that will not be cached:' % args.excluded_paths)

    host, port = args.local.split(':')

    if not args.distant.startswith('http://'):
        args.distant = 'http://%s' % args.distant

    logger.info('Starting httpcache proxy. Listening on %s, proxying to %s' %
                (args.local, args.distant))
    try:
        proxy = WSGIProxyApp(args.distant)
        app = CacheRequests(proxy, cache=cache, statsd=statsd,
                            cache_timeout=args.cache_timeout,
                            excluded_paths=args.excluded_paths, logger=logger)

        httpserver.serve(app, host, port=port)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        logger.info('Exiting, bye!')


if __name__ == '__main__':
    main()
