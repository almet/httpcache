import argparse
import sys

from gevent.pywsgi import WSGIServer
from gevent import monkey

from httpcache.webproxy import Application
from httpcache.utils import configure_logger, LOG_LEVELS
from httpcache import logger


def get_args():
    parser = argparse.ArgumentParser(description='An HTTP proxy, with cache.')

    parser.add_argument('--local', default='localhost:9201',
                        help='host/port of the local proxy')
    parser.add_argument('--distant', default='localhost:9200',
                        help='host/port of the distant server')
    parser.add_argument('--cache', action='store_true', default=False,
                        help='set to true if you want to use cache')
    parser.add_argument('--cache-server', default='localhost:11211')

    log_levels = LOG_LEVELS.keys() + [key.upper() for key in LOG_LEVELS.keys()]
    parser.add_argument('--log-level', dest='loglevel', default='info',
                        choices=log_levels, help="log level")

    parser.add_argument('--log-output', dest='logoutput', default='-',
                        help="log output")
    return parser.parse_args()


def main():

    monkey.patch_all()  # don't monkey patch unless we use this 'main' function
    args = get_args()

    cache = None
    if args.cache:
        import pylibmc
        cache = pylibmc.Client([args.cache_server])

    configure_logger(logger, args.loglevel, args.logoutput)

    app = Application('http://%s' % args.distant, cache)
    proxy = WSGIServer(args.local, app)
    logger.info('Starting httpcache proxy. Listening on %s, proxying to %s' %
                (args.local, args.distant))
    try:
        proxy.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        logger.info('Exiting, bye!')


if __name__ == '__main__':
    main()
